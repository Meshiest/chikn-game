## Chikn  
*A game about chickens fighting on a platform*

![](http://i.imgur.com/g2oSQ1w.png)

----

### Requirements
*  [python2.7 32bit](https://www.python.org/downloads/release/python-2711/)
*  [pygame](https://www.pygame.org/wiki/GettingStarted)

----

### Getting Started

#### Ubuntu
Install pygame

`sudo apt-get install python-pygame`

Install xbox-drv [optional, for using controllers]

```term
sudo apt-add-repository -y ppa:rael-gc/ubuntu-xboxdr  
sudo apt-get update  
sudo apt-get install ubuntu-xboxdrv
```

#### Windows
Install python2.7 32bit and pygame using [a pygame installer](http://www.pygame.org/download.shtml)

----

### Run

`pythonw chickn.py` (SDL makes a ton of debug messages that lag in windows)

----

### Controls (Up to 13 players simultaneously!!)

#### General
 * "up" -> Jump, Join Lobby & Change Color
 * "down" -> Slam / Charge launch, Leave Lobby
 * "left" -> Move Left
 * "right" -> Move Right

Keyboard: WASD, IJKL, ArrowKeys

Joystick: Leftstick -> 'left' & 'right', A -> 'up', and B -> 'down'

Bots: 0-9 keys will add a bot. The bots are **really** strong.

#### Menu

Keyboard: Escape -> Back, Enter -> Select

Joystick: Select -> Back, Start- > Enter (sometimes this changes to triggers?)

----

### Contributing

Please document!

I'll try to review pull requests as soon as I can!

----

### Screenshots

![](http://i.imgur.com/CDKdc4j.png)

![](http://i.imgur.com/g2oSQ1w.png)

![](http://i.imgur.com/LAgy61b.png)
