import pygame, math

effects = [] # stores the feathers

class Feather:
    def __init__(self, x, y, vx, vy, color=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.dir = -math.copysign(1, vx)
        self.theta = -math.pi/2
        self.color = color or (255, 255, 255)

    def tick(self, delta):
        self.x += self.vx * delta
        self.y += self.vy * delta
        self.vx *= (1-delta/2)
        self.vy += 100 * delta
        #self.vy = max(self.vy, -40)
        self.theta += math.pi*delta*self.dir
        if self.theta < -math.pi and self.dir == 1:
            self.dir = -1
        elif self.theta > 0 and self.dir == -1:
            self.dir = 1

    def draw(self, scr):
        offX = math.cos(self.theta) * 20
        offY = -math.sin(self.theta) * 10 

        pygame.draw.rect(scr, self.color, (self.x+offX, self.y+offY, 10, 5))
