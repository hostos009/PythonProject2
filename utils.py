import random
from typing import List, Generator
from settings import *

# Логіка генерації рівнв та збереження
#
def ensure_level_files():
    if not os.path.exists(LEVELS_DIR):
        os.makedirs(LEVELS_DIR)

    for level_num, config in LEVEL_CONFIG.items():
        file_path = os.path.join(LEVELS_DIR, f"level_{level_num}.txt")
        if not os.path.exists(file_path):
            create_random_level(file_path, config["size"])


def create_random_level(path: str, size: int):
    grid = [[BLOCK_TYPES["EMPTY"] for _ in range(size)] for _ in range(size)]

    for x in range(size):
        grid[0][x] = BLOCK_TYPES["STEEL"]
        grid[size - 1][x] = BLOCK_TYPES["STEEL"]
    for y in range(size):
        grid[y][0] = BLOCK_TYPES["STEEL"]
        grid[y][size - 1] = BLOCK_TYPES["STEEL"]

    placed_steel = 0
    while placed_steel < 6:
        rx, ry = random.randint(1, size - 2), random.randint(1, size - 2)
        if grid[ry][rx] == BLOCK_TYPES["EMPTY"]:
            grid[ry][rx] = BLOCK_TYPES["STEEL"]
            placed_steel += 1

    total_cells = size * size
    target_bricks = int(total_cells * 0.12)
    placed_bricks = 0

    while placed_bricks < target_bricks:
        rx, ry = random.randint(1, size - 2), random.randint(1, size - 2)
        if grid[ry][rx] == BLOCK_TYPES["EMPTY"]:
            grid[ry][rx] = BLOCK_TYPES["BRICK"]
            placed_bricks += 1

    px, py = size // 2, size - 2
    grid[py][px] = BLOCK_TYPES["PLAYER"]

    for dy in [-1, 0]:
        for dx in [-1, 0, 1]:
            nx, ny = px + dx, py + dy
            if (nx, ny) == (px, py):
                continue
            if 0 < nx < size - 1 and 0 < ny < size - 1:
                grid[ny][nx] = BLOCK_TYPES["BRICK"]

    with open(path, "w") as f:
        for row in grid:
            f.write("".join(row) + "\n")


def level_line_generator(file_path: str) -> Generator[str, None, None]:
    try:
        with open(file_path, "r") as f:
            for line in f:
                yield line.strip()
    except FileNotFoundError:
        print(f"File {file_path} not found.")


def load_level_matrix(level_num: int) -> List[List[str]]:
    path = os.path.join(LEVELS_DIR, f"level_{level_num}.txt")
    matrix = []
    if not os.path.exists(path):
        ensure_level_files()

    for line in level_line_generator(path):
        matrix.append(list(line))
    return matrix


def load_highscore() -> float:
    try:
        with open(SCORE_FILE, "r") as f:
            val = float(f.read())
            return val
    except (FileNotFoundError, ValueError):
        return 9999.0


def save_highscore(time_val: float):
    current_best = load_highscore()
    if time_val < current_best:
        with open(SCORE_FILE, "w") as f:
            f.write(str(round(time_val, 2)))