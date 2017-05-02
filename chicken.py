import pygame, math, random, time

from constants import *
from feather import *

objects = []

class Chicken:
	def __init__(self, x, y, controller, color):
		self.controller = controller # joy? kb? bot?

		self.x = self.initX = x # spawning positions
		self.y = self.initY = y
		
		self.color = color # player color
		self.lives = maxLives # number of lives left, maxLives is a constant
		self.killData = [] # wins, deaths, kills, updated in chikn.py when players are killed

		self.fitness = 0 # for machine learning

		self.size = 40 # width/height
		
		self.reset() # set initial values


	def reset(self):

		self.living = self.lives > 0
		
		# move player away if it has no lives
		self.x = not self.living and -10000 or self.initX
		self.y = self.initY

		# no initial movement
		self.vx = self.vy = 0

		# slam variables
		self.slam = False # player is slamming
		self.crouchEnd = 0 # time since player was crouched on the ground (0 the moment of impact)
		self.groundTime = 0
		# one tick history of key['down']
		self.lastSlam = False
		
		# facing direction
		self.lastDir = 1

		# time since the player flapped (at death) and spawn time
		self.lastFlap = self.spawnTime = time.time()
		# one tick history of key['up']
		self.flapDown = False

		# seconds of holding down while on the ground, max at 3 (should make a constant)
		self.charge = 0

		# Amount of damage done
		self.damageMod = 1

		# last player to slam/touch this player
		self.attacker = self

		# spawn some feathers
		for i in range(10):
			angle = random.random() * math.pi * 2
			power = random.random() * 200 + 100
			effects.append(Feather(
				self.x,
				self.y-self.size/2,
				math.cos(angle)*power,
				math.sin(angle)*power,
				random.random() < 0.2 and self.color or None)
			)
 

	def canJump(self):

		# player is falling
		if self.vy > abs(0.1):
			return False

		# player is vertically on the platform
		if self.y != HEIGHT-platform_height:
			return False

		# player is horizontally on the platform
		return self.x > WIDTH/2-platform_width/2-self.size/2 and self.x < WIDTH/2+platform_width/2+self.size/2

	# Get the nearest chiken
	def nearest(self):
		distance = 1000 * self.size
		near = False
		for obj in objects:
			if obj == self or not obj.living:
				continue

			dist = math.hypot(self.x-obj.x, self.y-obj.y)
			if dist < distance:
				near = obj
				distance = dist

		return near

	# all the nearest chickens
	def nearArr(self, distance):
		near = []
		for obj in objects:
			if obj == self:
				continue

			dist = math.hypot(self.x-obj.x, self.y-obj.y)
			if dist < distance:
				near.append(obj)

		return near

	# Push this chicken away from other chickens
	def forceAway(self, obj, maxDist, bonus):
		maxDist += obj.size/2
		dist = math.hypot(self.x-obj.x, self.y-obj.y-obj.size/4)
		if dist > maxDist:
			return


		theta = math.atan2(self.y-obj.y-obj.size/4, self.x-obj.x)
		coeff = 10
		coeff *= self.damageMod
		if self.charge > 0:
			coeff += self.charge
		xVel = math.cos(theta)*((maxDist-dist)*coeff)
		yVel = math.sin(theta)*((maxDist-dist)*coeff)
		self.vx += xVel
		self.vy += yVel

		# spawn some feathers
		for i in range(5):
			angle = random.random() * math.pi * 2
			power = random.random() * 200 + 100
			effects.append(Feather(
				self.x,
				self.y-self.size/2,
				math.cos(angle)*power - xVel / 3,
				math.sin(angle)*power - yVel / 3,
				random.random() < 0.5 and self.color or None)
			)

		# Update damage mod with new damage
		damage = 1 - dist / maxDist + bonus
		self.damageMod += damage * DAMAGE_CONST

	def boost(self):
		if self.charge > 0.25:
			jumpSound.play()
			self.vy -= self.size*10*self.charge
		self.charge = 0


	def slamExplode(self):
		for i in range(3):
			effects.append(Feather(self.x,self.y-5,random.random()*100-50,-random.random()*150-30))


	def tick(self, delta, keys):

		if self.spawnTime + spawnTimeout > time.time():
			if(keys['left']):
				self.lastDir = -1

			if(keys['right']):
				self.lastDir = 1
			
			if keys['down']:
				self.crouchEnd = time.time()
			return

		if(keys['left'] and self.vx > -5 * self.size):
			self.vx += -40*delta * self.size
			self.lastDir = -1

		if(keys['right'] and self.vx < 5 * self.size):
			self.vx += 40*delta * self.size
			self.lastDir = 1

		if(keys['up'] and self.canJump() and not self.slam):
			self.vy = -7.5*self.size
			jumpSound.play()
			self.lastJump = time.time()

		if(keys['up'] and self.y > HEIGHT-platform_height+60 and self.vy > 10 and self.lastFlap + 0.2 < time.time() and not self.flapDown):
			self.flapDown = True
			self.vy = -10
			flapSound.play()
			self.lastFlap = time.time()
			effects.append(Feather(self.x,self.y-5,random.random()*100-50,-random.random()*150-30))
		elif not keys['up']:
			self.flapDown = False


		if keys['down'] and not self.slam and not self.lastSlam and time.time() - self.groundTime > SLAM_COOLDOWN:
			self.lastSlam = True
			if not self.canJump(): 
				self.slam = True
				self.vy = 20 * self.size
				startSlamSound.play()

		self.charge = min(self.charge, 2)

		if not keys['down']:
			self.lastSlam = False
			if self.charge > 0.25:
				self.boost()
		elif self.canJump():
			self.crouchEnd = time.time()

		if not self.canJump() and self.charge > 0:
			self.boost()


		for obj in objects:
			if obj == self:
				continue

			dist = math.hypot(self.x-obj.x, self.y-obj.y)
			theta = math.atan2(self.y-obj.y, self.x-obj.x)
			netX = self.vx + obj.vx
			netY = self.vy + obj.vy
			minDist = self.size/2+obj.size/2

			if dist < minDist:
				# push players if they're inside of eachother
				self.x += (minDist-dist)*math.cos(theta) * self.damageMod
				self.y += (minDist-dist)*math.sin(theta) * self.damageMod
				obj.x += (minDist-dist)*math.cos(theta+math.pi) * obj.damageMod
				obj.y += (minDist-dist)*math.sin(theta+math.pi) * obj.damageMod
				# bounce players away on x axis
				self.vx = netX/2
				obj.vx = -netX/2

				# assign attackers, if players are grounded, this will do nothing
				obj.attacker = self
				self.attacker = obj

		self.x += self.vx*delta
		self.y += self.vy*delta
		onPlatform = abs(WIDTH/2-self.x) < platform_width/2+self.size/2

		# distance and direction of player from middle of platform
		dist = self.x-WIDTH/2
		direction = math.copysign(1,dist)

		# time from last slam land or crouch
		crouchDelta = time.time() - self.crouchEnd
		
		# add gravity
		self.vy += 400*delta    
		if self.y >= HEIGHT-platform_height: # player is above the platform
			if onPlatform and self.y < HEIGHT-platform_height+50: # player is touching the platform
				# slow down the player through friction
				self.vx = self.vx - self.vx*10*delta 

				if abs(self.vx) < 0.5: # if the player stops, they aren't being attacked
					self.attacker = self

				if self.slam: # check if the player is slamming and push away nearby players
					self.slam = False
					bonusPower = max((self.vy-800)/12, 0)
					self.fitness += bonusPower + self.size*2
					near = self.nearArr(self.size*2)
					slamSound.play()
					for obj in near:
						obj.attacker = self
						obj.forceAway(self, self.size*2+bonusPower, bonusPower/15)

					self.crouchEnd = time.time()
					self.groundTime = time.time()

				# stop the player to prevent falling through the platform
				if self.vy > 0:
					self.vy = 0

				# make the player be locked to the platform
				self.y = HEIGHT-platform_height

				# if player is no longer crouching
				if crouchDelta > 0.05:
					self.charge = 0
				else:
					self.charge += delta


			else:
				if abs(dist) < platform_width/2+self.size/2: # player is on the platform, but underneath it
					self.x = WIDTH/2+direction*(platform_width/2+self.size/2) # push the player outside of the platform
					if self.vx * direction > 0: 
						self.vx = 0; # remove the player's velocity if it's going into the platform



	def draw(self, scr):

		# time since last slam
		crouchDelta = time.time() - self.crouchEnd

		# size of waddle
		waddleScale = min((time.time() - self.groundTime) / SLAM_COOLDOWN, 1)

		# player is slamming
		isSlamming = self.slam and self.vy > 20 * self.size

		if self.x < 0 or self.x > WIDTH or self.y < 0:
			pygame.draw.rect(scr, self.color, (
				sorted([20, self.x, WIDTH-20])[1]-10 * (isSlamming and 0.5 or 1),
				max(self.y, 20)-10,
				20 * (isSlamming and 0.5 or 1),
				20
			))
			return

		# base rectangle for the body of the chicken
		body = isSlamming and ( #slam body
			self.x - self.size/4.0,
			self.y - self.size,
			self.size/2.0,
			self.size
		) or crouchDelta < 0.1 and ( #squashed body
			self.x - self.size/2.0,
			self.y - self.size/4.0 - (self.size/4.0*3)*((crouchDelta/0.1)**2),
			self.size,
			self.size/4.0 + (self.size/4.0*3)*((crouchDelta/0.1)**2)
		) or ( # regular square body
			self.x - self.size/2.0,
			self.y - self.size,
			self.size,
			self.size
		)

		# rectangle for the bill
		bill = (
			self.x-self.size/4+self.lastDir*(body[2]/2+self.size/4),
			body[1]+body[3]/4.0,
			self.size/2.0,
			body[3]/4.0
		)

		# rectangle for the waddle 
		waddleHeight = body[3]/2.0 * waddleScale
		waddle = (
			self.x-self.size/8+self.lastDir*(body[2]/2+self.size/8),
			body[1]+body[3]/2.0,
			self.size/4,
			waddleHeight
		)

		# drawing the rectangles that make up the chicken
		pygame.draw.rect(scr, (255, 255, 255), body)
		pygame.draw.rect(scr, (255, 200, 30), bill)
		pygame.draw.rect(scr, self.color, waddle)

		if self.charge > 0.25:
			pygame.draw.rect(scr, self.color, (
				body[0]+body[2]/2-self.size/4,
				body[1]+body[3],
				self.size/2,
				((self.charge-0.25) * 5) ** 1.5
			))

		# draw the weird top waddle thing on a chicken
		headWidth = body[2]/4
		for i in range(3):
			headHeight = (self.size/5)*body[3]/self.size*(i+1) * self.damageMod
			pygame.draw.rect(scr, self.color, (
				self.x-headWidth*((self.lastDir+1)/2)+(headWidth*(i))*self.lastDir,
				body[1]-headHeight,
				headWidth,
				headHeight
			))

		# check if there's a nearby enemy
		near, nearX, nearY = self.nearest(), 0, 0

		if near: # point the eyes slightly towards the enemy
			theta = math.atan2(near.y-self.y, near.x-self.x)
			nearX = math.cos(theta) / 10.0 * self.size
			nearY = math.sin(theta) / 10.0 * self.size

		# rectangle for eye
		eyeSize = self.size/6 * self.damageMod
		eye = (
			self.x+body[2]/4*self.lastDir-eyeSize/2+nearX,
			body[1]+body[3]/4.0-eyeSize/2+nearY,
			eyeSize,
			eyeSize
		)

		# draw the eye
		pygame.draw.rect(scr, (0, 0, 0), eye)

		# time since the spawn
		deltaSpawn =  spawnTimeout - time.time() + self.spawnTime
		if deltaSpawn > 0: #render the cage
			pygame.draw.rect(scr, (50, 50, 50), (self.x - self.size/2 - 5, self.y - 5, self.size + 10, 5))
			if deltaSpawn > 0.5: # start animating bars 0.5 seconds after spawning 
				deltaSpawn = 0.5
			for i in range(5): # draw bars of the cage
				pygame.draw.rect(scr, (50, 50, 50), (
					self.x - (self.size + 10)/2 + ((self.size + 10 - 5)/4.0) * i,
					self.y - (self.size*2 + 20) * deltaSpawn,
					5,
					(self.size*2 + 20) * deltaSpawn)
				)
