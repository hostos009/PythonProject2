import pygame
import os

TILE_SIZE = 50
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (127, 127, 127)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 200)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)

PLAYER_SPEED = 4
PLAYER_HP = 3
SHOOT_DELAY = 1000

LEVEL_CONFIG = {
    1: {"size": 20, "enemies": 4},
    2: {"size": 20, "enemies": 6},
    3: {"size": 20, "enemies": 9},
}

BLOCK_TYPES = {
    "EMPTY": ".",
    "BRICK": "#",
    "STEEL": "@",
    "PLAYER": "p",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEVELS_DIR = os.path.join(BASE_DIR, "levels")
SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")