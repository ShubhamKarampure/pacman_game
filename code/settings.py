import pygame, math, sys, time
import numpy as np

# ! WINDOW SETTINGS (480 x 608 pixels)
WWID = 480  # WINDOW WIDTH
WHGT = 608  # WINDOW HEIGHT
FRT = 120  # FRAME RATE
WOFST = 48  #

# ! TITE SETTING ( 16 x 16 pixels)
TWID = 16
THGT = 16
TWOFST = 8
THOFST = 8

# ! MAP SETTINGS [(33x16) by (30x16) pixels)
map = np.loadtxt("maze.txt", dtype="<U1")

# ! LEVELS
frighten_duration = 6
levels = {
    1: [
        {7, 20}
    ]
}

# ! DIRECTION SETTING
STOP = -1
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3
PORTAL = 4

OPPOSITE_DIRECTION = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

# ! TIME SETTING
ON = 1
OFF = 0

# ! PLAYER SETTING ( 16 x 16 pixels)
speed = 1
player_spawn = (16, 24)

# ! Ghost Setting
fudge = 15
eye = 2
die = 1
SCATTER = 0
CHASE = 1
FRIGHTEN = 0
BRAVE = 1
GHOSTHOUSE = (2, 2)
GHOSTEXIT = (2,0)
homedata = np.loadtxt("homedata.txt", dtype="<U1")

# ! Blinky Setting
blinkyspeed = 1
blinky_spawn = (13, 12)
blinkyhome = 500, 0

# ! Pinky Setting
pinkyspeed = 1
pinky_spawn = (13, 12)
pinkyhome = 0, 0
pinky_fudge = {UP: (-50, -50), DOWN: (0, +50), LEFT: (-50, 0), RIGHT: (+50, 0)}


# ! Pinky Setting
inkyspeed = 1
inky_spawn = (13, 12)
inkyhome = 500, 600
inky_fudge = {UP: (0, -50), DOWN: (0, +50), LEFT: (-50, 0), RIGHT: (+50, 0)}

# ! Clyde Setting
clydespeed = 1
clyde_spawn = (13, 12)
clydehome = (0, 600)
clyde_fudge = {UP: (0, -50), DOWN: (0, +50), LEFT: (-50, 0), RIGHT: (+50, 0)}



