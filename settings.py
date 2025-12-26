import os

# Загальне про розміри клітинки, фпс та кольори
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

# Швидкість користувача, хп, затримка пострілу
PLAYER_SPEED = 4
PLAYER_HP = 3
SHOOT_DELAY = 1000

# конфіг для розмірів полей та кількості противників для кожного з рівнів
LEVEL_CONFIG = {
    1: {"size": 20, "enemies": 4},
    2: {"size": 20, "enemies": 6},
    3: {"size": 20, "enemies": 9},
}

# Опис блоків
BLOCK_TYPES = {
    "EMPTY": ".",
    "BRICK": "#",
    "STEEL": "@",
    "PLAYER": "p",
}
# Визначення папки скрипту, шляхи до папок рівнів та рекордів
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEVELS_DIR = os.path.join(BASE_DIR, "levels")
SCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")