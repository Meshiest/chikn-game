import pygame

WIDTH, HEIGHT = 1400, 800

BLACK = (0, 0, 0)
SKY_COLOR = (190, 200, 255)
GRASS_COLOR = (20, 100, 20)
DIRT_COLOR = (90, 60, 30)

platform_width = 300
platform_height = 160

maxLives = 3

spawnTimeout = 5

BTN_A = 0
BTN_B = 1
BTN_X = 2
BTN_Y = 3
BTN_LB = 4
BTN_RB = 5
BTN_SELECT = 6
BTN_START = 7
BTN_LSTICK = 8
BTN_RSTICK = 9
BTN_LEFT = 'L'
BTN_RIGHT = 'R'


colors = [
    (190, 30, 30), # red
    (230, 190, 30),  # orange
    (230, 230, 30),  # yellow
    (30, 100, 30),  # green
    (30, 230, 230), # cyan
    (30, 30, 190), # blue
    (230, 30, 230), # magenta
    (100, 30, 100),  # purple
    (230, 150, 190),  # pink
    (120, 80, 40),  # brown
    (230, 230, 230),  # white
    (100, 100, 100),  # grey
    (30, 30, 30),  # black
]

# fonts

playerListFont = pygame.font.Font("./font/Dosis-ExtraBold.ttf", 40)
titleFont = pygame.font.Font("./font/Dosis-ExtraBold.ttf", 80)

jumpSound = pygame.mixer.Sound('./audio/jump.wav')
deathSound = pygame.mixer.Sound('./audio/death.wav')
flapSound = pygame.mixer.Sound('./audio/flap.wav')
slamSound = pygame.mixer.Sound('./audio/slam.wav')
startSlamSound = pygame.mixer.Sound('./audio/slam_start.wav')
joinSound = pygame.mixer.Sound('./audio/join_lobby.wav')
leaveSound = pygame.mixer.Sound('./audio/leave_lobby.wav')
selectSound = pygame.mixer.Sound('./audio/select.wav')
confirmSound = pygame.mixer.Sound('./audio/confirm.wav')