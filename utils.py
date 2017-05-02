import pygame, time

from bot import *
from chicken import *

keyboards = [{
    'up': pygame.K_w,
    'left': pygame.K_a,
    'down': pygame.K_s,
    'right': pygame.K_d,
}, {
    'up': pygame.K_UP,
    'left': pygame.K_LEFT,
    'down': pygame.K_DOWN,
    'right': pygame.K_RIGHT,
}, {
    'up': pygame.K_i,
    'left': pygame.K_j,
    'down': pygame.K_k,
    'right': pygame.K_l,
}]
keyboardNames = [
    'WASD',
    'ArrowKeys',
    'IJKL',
]

def initJoysticks():
    if pygame.joystick.get_init():
        pygame.joystick.quit()

    pygame.joystick.init()
    for i in range(pygame.joystick.get_count()):
        print("Initializing joy%i"%(i))
        joy = pygame.joystick.Joystick(i)
        joy.init()


def getControls(controller, keys): # returns a hash of keys to the appropriate controller
    arr = {
        'up': False,
        'down': False,
        'left': False,
        'right': False,
    }

    if controller.startswith("kb"): # handle input for keyboards
        keyboard = keyboards[int(controller[2:])]
        for key, val in keyboard.iteritems():
            arr[key] = keys[val]

    elif controller.startswith("joy"): # handle input for controllers
        joy = pygame.joystick.Joystick(int(controller[3:]))
        arr['up'] = joy.get_button(0)
        arr['down'] = joy.get_button(1)
        axis = joy.get_axis(0)
        arr['left'] = abs(axis) > 0.5 and axis < 0
        arr['right'] = abs(axis) > 0.5 and axis > 0

    elif controller.startswith("bot"):
        arr = getBotMovement(controller)

    return arr

def displayPlayerName(controller):
    name = ""

    if controller.startswith("kb"): # handle input for keyboards
        keyboard = int(controller[2:])
        name = keyboardNames[keyboard]

    elif controller.startswith("joy"): # handle input for controllers
        joy = int(controller[3:])
        name = "joy %i"%(joy+1)

    elif controller.startswith("bot"): # handle input for bot
        bot = int(controller[3:])
        name = "bot %i"%(bot)

    return name

def drawLife(screen, x, y, color, negative=False):

    if negative == "win":
        pygame.draw.circle(screen, (255, 255, 255), (int(x), int(y)), 13)
        pygame.draw.circle(screen, (255, 255, 0), (int(x), int(y)), 10)

        return

    # white border
    pygame.draw.rect(screen, 
        negative and (0, 0, 0) or (255, 255, 255), (
            x - 13,
            y - 13,
            26,
            26
        )
    )

    # colored middle
    pygame.draw.rect(screen, color, (
        x - 10,
        y - 10,
        20,
        20
    ))