import pygame, math, json, os, copy

from chicken import *
from constants import *

# screen for debug drawing
screen = pygame.display.get_surface()

def saveBrain():
    print ""

# returns the controls for the bot
def getBotMovement(controller):

    arr = { # empty controls array
        'up': False,
        'down': False,
        'left': False,
        'right': False,
    }
    
    bot = playerFromController(controller)

    if not bot: 
        return


    height = HEIGHT - platform_height - bot.y
    offX = bot.x - WIDTH/2

    near = bot.nearest()
    dist = near and math.hypot(near.x-bot.x, near.y-bot.y) or 10000
        
    if abs(offX) > 10 and dist > 100:
        if offX < 0:
            arr['right'] = True
        else:
            arr['left'] = True


    if height >= 0 and height < 30:
        if near:
            if dist < 60 and bot.canJump():
                arr['up'] = True

    dist = 5000
    close = None
    for obj in objects:
        if obj == bot or not obj.living:
            continue

        if abs(obj.x - WIDTH/2) > platform_width/2+obj.size/2:
            continue

        if height > 30:
            if abs(obj.x - bot.x) < 40:
                if obj.y > HEIGHT-platform_height-20 and obj.y <= HEIGHT-platform_height and not bot.slam:
                    arr['down'] = True

                if abs(obj.y - bot.y) < 10:
                    arr['down'] = True

        if abs(obj.x - bot.x) < dist:
            dist = abs(obj.x - bot.x)
            close = obj

    if close:
        if bot.x < close.x - 10:
            arr['right'] = True

        if bot.x > close.x + 10:
            arr['left'] = True

        if close.vy > 10 and bot.canJump():
            arr['up'] = True

    if abs(offX) > platform_width/2+bot.size/2:

        if offX < 0:
            arr['right'] = True
        else:
            arr['left'] = True

    return arr


# the rest of the code from here on is unused, but kept for future machine learning implementations

# different values for the matrix
AIR = 0
GROUND = 1
PLAYER = 2
SLAM = 3

COLORS = [
    (255, 255, 255),
    (0, 0, 0),
    (255, 0, 0),
    (255, 255, 0)
]

VIEW_RADIUS = 3 # how far the brain can see


# all of the variables for machine learning
buttons = ['up', 'down', 'left', 'right']


# gets a player from a given controller
def playerFromController(controller): 
    player = None
    for obj in objects:
        if obj.controller == controller:
            player = obj
            break

    return player


def learnMovement(controller, keys):
    global LEARNING

    if not LEARNING: return
    environment = getEnvironment(playerFromController(controller))
    out = []
    for b in buttons:
        out.append(keys[b] and 1 or 0)
    ds.addSample(environment, out)
    print "Training"
    trainer.train()
    
def getEnvironment(bot):
    environment = [bot.vx, bot.vy]
    for y in range(-VIEW_RADIUS, VIEW_RADIUS+1): # fill a 2d array with the surroundings
        for x in range(-VIEW_RADIUS, VIEW_RADIUS+1):
            environment.append(getData(bot, bot.x+x*40, bot.y+y*40))

    return environment

def getData(bot, x, y): # return an id for whatever is at that point
    if x > WIDTH/2-platform_width/2 and x < WIDTH/2+platform_width/2 and y > HEIGHT-platform_height:
        return GROUND

    for obj in objects:
        if obj != bot:
            if math.hypot(obj.x-x, obj.y-y) < 20:
                return obj.slam and SLAM or PLAYER

    return AIR
