import sys, pygame, time, math, random

pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# import my own code
from constants import *

screen = pygame.display.set_mode([WIDTH, HEIGHT]) #, pygame.RESIZABLE, 32)

from feather import *
from chicken import *
from utils import *
from bot import * 


winner = None

tick = time.time()
lastTick = tick

lastSpawn = time.time()

lastMenu = -1
MENU_EXIT = -1
MENU_MAIN = 0
MENU_PLAY = 1
MENU_JOIN = 2
MENU_WIN = 3
menu = MENU_MAIN

mainMenu = ['Play','Quit']
mainMenuCurr = 0
mainMenuPos = 0

players = []
allocatedColors = {}
endData = {}

def reset():
    global lastSpawn
    lastSpawn = time.time()
    del effects[:]

    for obj in objects:
        obj.reset()


def drawGame(keys):
    pygame.draw.rect(screen, SKY_COLOR, (0, 0, WIDTH, HEIGHT))
    pygame.draw.rect(screen, DIRT_COLOR, ( # draw the dirt
        WIDTH/2-platform_width/2,
        HEIGHT-platform_height,
        platform_width,
        platform_height
    ))

    pygame.draw.rect(screen, GRASS_COLOR, ( # draw the grass
        WIDTH/2-platform_width/2,
        HEIGHT-platform_height,
        platform_width,
        50
    ))

    resetLives = playersLeft = len(objects)

    lastPlayer = False
    for obj in objects:
        if not obj.living:
            playersLeft -= 1 # remove player from living player count
            if obj.lives < 1:
                resetLives -= 1 # remove player from players with lives

            continue

        # set the last player to current obj, if resetLives == 1, this is the last player

        obj.tick(delta, getControls(obj.controller, keys))

        # set the player to not living if it is off screen
        if obj.y > HEIGHT + 50:
            for i in range(10):
                angle = -random.random() * math.pi / 2 - math.pi/4
                power = random.random() * 200 + 100
                effects.append(Feather( # spawn a new feather
                    obj.x,
                    obj.y-obj.size/2,
                    math.cos(angle)*power,
                    math.sin(angle)*power,
                    random.random() < 0.2 and obj.color or None)
                )
            obj.attacker.killData.append(("kill",obj.color))
            obj.killData.append(("death",obj.attacker.color))

            obj.lives -= 1 # remove a life and kill the player
            obj.living = False
            deathSound.play()
            playersLeft -= 1
            if obj.lives < 1:
                resetLives -= 1

        if obj.lives > 0 and obj.living:
            lastPlayer = obj

    if resetLives <= 1: # if there's one player with lives, give everyone more lives
        
        global winner, menu, endData

        endData = {} # clear the last scoreboard

        for obj in objects: # add kills and deaths to the scoreboard
            endData[obj.controller] = obj.killData[:]

        if lastPlayer:
            lastPlayer.killData.append(("win", (0, 0, 0)))

            # the winner is the controller of the last player
            winner = lastPlayer.controller

        del objects[:]

        global menu
        menu = MENU_WIN # change the menu to the win menu
        return

    if playersLeft <= 1: # reset if there is one player left
        if playersLeft > 0:
            lastPlayer.killData.append(("win", (0, 0, 0)))

        reset()
        return

    for obj in effects:
        obj.tick(delta)
        if obj.y > HEIGHT+50: # remove effects that are off screen
            effects.remove(obj)
    
    count = len(objects)
    part = WIDTH*2/3.0/(count) # take a fraction of two thirds of the screen for lives
    for obj in objects:
        if obj.lives < 1:
            continue
        
        if obj.living:
            obj.draw(screen)

        pos = objects.index(obj)

        # position where center of lives should be displayed
        centerX = WIDTH/2-(len(objects)/2.0-pos-0.5)*part

        # draw the lives of the players
        for i in range(obj.lives):
            
            #pygame.draw.rect(screen, (0, 0, 0), (centerX, 0, 1, HEIGHT))

            drawLife(screen, # draw a life
                centerX+part/maxLives/3*(2*i+1-obj.lives),
                HEIGHT - 20,
                obj.color
            )


    for obj in effects:
        obj.draw(screen)

    spawnDelta = spawnTimeout - time.time() + lastSpawn
    if spawnDelta > 0:
        text = playerListFont.render(str(int(round(spawnDelta))), 1, (10, 10, 10))
        rad = (((spawnDelta+0.5) % 1)*4)**2 + 20
        pygame.draw.rect(screen, (255, 255, 255), (WIDTH/2-rad, 100+text.get_height()/2-rad, rad*2, rad*2))
        screen.blit(text, (WIDTH/2-text.get_width()/2, 100))

def nextAvailableColor(color=None):
    # if a color in the list is given, shift the colors to that index, otherwise use all colors
    openColors = colors.count(color) != 0 and colors[colors.index(color):]+colors[:colors.index(color)] or colors[:]

    for player in players: # go through all players and remove colors that are in use

        playerColor = allocatedColors[player]
        if openColors.count(playerColor) > 0:
            openColors.remove(playerColor)

    if len(openColors) > 0: # if there are any more open colors
        return openColors[0]
    elif colors.count(color) != 0: # if the original color exists
        return color
    else:
        return colors[0] 

def drawJoinMenu(keys): 

    for i in range(len(keyboards)): # handle keyboards joining
        keyboard = keyboards[i]
        name = "kb%i" % (i)
        if players.count(name) == 1:  # player is in lobby
            if keys.get(keyboard['down']): # keyboard press down
                del allocatedColors[name] # remove player
                players.remove(name) 
                leaveSound.play()

            else:
                if keys.get(keyboard['up']):
                    allocatedColors[name] = nextAvailableColor(allocatedColors[name])

        else:
            if keys.get(keyboard['up']): # keyboard press up
                allocatedColors["kb%i" % (i)] = nextAvailableColor()
                players.append("kb%i" % (i))
                joinSound.play()


    for i in range(pygame.joystick.get_count()): # handle controllers joining
        name = "joy%i"%(i)
        if players.count(name) == 1: # player is in lobby
            if keys['joy'].get("joy%i_%i" % (i, BTN_B)): # controller press B
                del allocatedColors[name]
                players.remove(name) # remove player
                leaveSound.play()

            else:
                if keys['joy'].get("joy%i_%i" % (i, BTN_A)):
                    allocatedColors[name] = nextAvailableColor(allocatedColors[name])

        else:
            if keys['joy'].get("joy%i_%i" % (i, BTN_A)): # controller press A
                allocatedColors[name] = nextAvailableColor()
                players.append(name)
                joinSound.play()

    for i in range(10):
        char = chr(i+48)
        name = "bot%s" % (char)
        if keys.get(48+i):
            if players.count(name) == 1:
                del allocatedColors[name]
                players.remove(name)
                leaveSound.play()
            else:
                allocatedColors[name] = nextAvailableColor()
                players.append(name)
                joinSound.play()
 
    pygame.draw.rect(screen, SKY_COLOR, (0, 0, WIDTH, HEIGHT))

    joinText = playerListFont.render("Press Jump to Join", 1, (255, 255, 255))
    screen.blit(joinText, (WIDTH/2 - joinText.get_width()/2, 10))

    if keys.get(pygame.K_p):
        global LEARNING
        
        LEARNING = not LEARNING
        print("LEARNING is "+str(LEARNING))

    tick = time.time()
    centerX = WIDTH/2
    centerY = HEIGHT/2

    playerCount = len(players)

    for i in range(playerCount):
        yOff = i * 30 + 80
        xOff = 10
        name = displayPlayerName(players[i])

        text = playerListFont.render(name, 1, (10, 10, 10))
        screen.blit(text, (xOff + 36, yOff-text.get_height()/2)) # draw text

        color = allocatedColors[players[i]]

        # white border
        pygame.draw.rect(screen, (255, 255, 255), (xOff, yOff-13, 26, 26))
        # colored middle
        pygame.draw.rect(screen, color, (xOff+3, yOff-10, 20, 20))

        theta = tick + math.pi*2/playerCount*i

        posX = centerX + math.cos(theta) * (playerCount * 10 + 20)
        posY = centerY + math.sin(theta) * (playerCount * 10 + 20)

        #pygame.draw.circle(screen, (255, 255, 255), (int(posX), int(posY)), 21)
        pygame.draw.ellipse(screen, color, (posX-18, posY-30, 36, 60))
        pygame.draw.rect(screen, SKY_COLOR, (posX-18, posY, 36, 30))
        pygame.draw.circle(screen, color, (int(posX), int(posY)), 18)


    playerCount = len(players)

    if (keys.get(pygame.K_RETURN) or keys['joy'].get(BTN_START)) and playerCount > 1:
        confirmSound.play()

 
        remainder = playerCount % 4 
        for i in range(playerCount):
            print("Adding player %s" % (players[i]))

            total = (i < playerCount - remainder and 4 or remainder) # num players on row
            part = platform_width*2/3.0/total # space between players

            centerX = WIDTH/2 - (i % 4 + 0.5 - total/2.0) * part
            posY = HEIGHT-platform_height-200 - i/4 * 60

            objects.append(Chicken(
                centerX,
                posY,
                players[i],
                allocatedColors[players[i]]
            ))

        global menu
        menu = MENU_PLAY

    if keys.get(pygame.K_ESCAPE) or keys['joy'].get(BTN_SELECT):
        menu = MENU_MAIN

def drawMainMenu(delta, keys):
    global menu, mainMenu, mainMenuCurr, mainMenuPos

    pygame.draw.rect(screen, SKY_COLOR, (0, 0, WIDTH, HEIGHT))

    titleText = titleFont.render("Chikn", 1, (255, 255, 255))
    screen.blit(titleText, (WIDTH/2 - titleText.get_width()/2, 80))

    if keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE) or keys['joy'].get(BTN_START):
        confirmSound.play()
        if mainMenu[mainMenuCurr] == 'Play':
            menu = MENU_JOIN

        elif mainMenu[mainMenuCurr] == 'Quit':
            menu = MENU_EXIT


    numOptions = len(mainMenu)

    if keys.get(pygame.K_w) or keys.get(pygame.K_UP) or keys['joy'].get(BTN_SELECT): # previous menu option
        mainMenuCurr = (mainMenuCurr + 1 + numOptions) % numOptions
        selectSound.play()

    if keys.get(pygame.K_s) or keys.get(pygame.K_DOWN): # next menu option
        mainMenuCurr = (mainMenuCurr - 1 + numOptions) % numOptions
        selectSound.play()

    mainMenuPos += (mainMenuCurr-mainMenuPos) * 10 * delta # translate towards selected option

    pygame.draw.rect(screen, (255, 255, 255), (0, HEIGHT/2-25, WIDTH, 50)) # draw a rectangle to hold the selected menu

    for i in range(numOptions):
        option = mainMenu[i]
        text = playerListFont.render(option, 1, (10, 10, 10))
        screen.blit(text, ( # draw the option
            WIDTH/2 - text.get_width()/2,
            HEIGHT/2 + (i-mainMenuPos) * 50 +  - text.get_height()/2)
        )




def drawWinMenu(keys):
    global menu

    winnerColor = winner and allocatedColors[winner] or SKY_COLOR

    playerCount = len(players)

    pygame.draw.rect(screen, SKY_COLOR, (0, 0, WIDTH, HEIGHT))
    scale = HEIGHT/10

    # draw large background egg
    pygame.draw.ellipse(screen, winnerColor, (WIDTH/2-3*scale, HEIGHT/2-5*scale*3/4, 6*scale, 10*scale))
    pygame.draw.rect(screen, SKY_COLOR, (WIDTH/2-3*scale, HEIGHT/2+5*scale/4, 6*scale, 5*scale))
    pygame.draw.circle(screen, winnerColor, (int(WIDTH/2), int(HEIGHT/2+5*scale/4)), 3*scale)

    part = WIDTH*2/3.0/playerCount
    vert = HEIGHT*2/3.0
    for i in range(playerCount):
        player = players[i]

        centerX = WIDTH/2 - (i + 0.5 - playerCount/2.0) * part

        left = centerX-part/3
        top = HEIGHT/2-vert/2 
        width = part*2/3
        roundedWidth = (int(width-15)/30*30)

        pygame.draw.rect(screen, (255, 255 ,255), ( # draw border
            left-3,
            top-3,
            width+6,
            vert+6
        ))

        pygame.draw.rect(screen, (allocatedColors[player]), ( # draw box
            left,
            top,
            width,
            vert
        ))

        killData = endData[player]
        for k in range(len(killData)):
            data = killData[k]
            drawLife(screen, 
                left + k*30 % roundedWidth + 30, 
                top + k*30/roundedWidth * 30 + 30,
                data[1],
                data[0] == "death" and True or data[0] == "win" and "win" or False
            )


    if keys.get(pygame.K_RETURN) or keys.get(pygame.K_SPACE) or keys['joy'].get(BTN_START):
        menu = MENU_JOIN

    elif keys.get(pygame.K_ESCAPE) or keys['joy'].get(BTN_SELECT):
        menu = MENU_MAIN
  

while 1:

    lastTick, tick = tick, time.time()
    delta = tick - lastTick

    keys = pygame.key.get_pressed()
    keyPressed = {'joy': {}}

    close = False
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            close = True

        if event.type == pygame.VIDEORESIZE: #not used
            WIDTH = event.dict['size'][0]
            HEIGHT = event.dict['size'][1]
            reset()
            #screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.HWSURFACE|pygame.DOUBLEBUF|pygame.RESIZABLE)

        keyPressed['joy'] = {}
        
        if event.type == pygame.KEYDOWN: # assign the key if it's down
            keyPressed[event.dict['key']] = True

        if event.type == pygame.JOYBUTTONDOWN: # assign the joy button twice (one for ambiguous presses)
            keyPressed['joy'][event.dict['button']] = True
            keyPressed['joy']["joy%i_%i" % (event.dict['joy'], event.dict['button'])] = True

    if close:
        saveBrain()
        break


    if menu != lastMenu: # when the menu changes
        lastMenu = menu

        if menu == MENU_MAIN:
            initJoysticks()
            continue

        if menu == MENU_PLAY:
            reset()


    if menu == MENU_MAIN:
        drawMainMenu(delta, keyPressed)

    elif menu == MENU_JOIN:
        drawJoinMenu(keyPressed)

    elif menu == MENU_PLAY:
        drawGame(keys)

        if keyPressed.get(pygame.K_ESCAPE): # return to join menu if pressed
            del objects[:] # remove players

            menu = MENU_JOIN

    elif menu == MENU_WIN:
        drawWinMenu(keyPressed)

    elif menu == MENU_EXIT:
        saveBrain()
        break
 
    pygame.display.update()
