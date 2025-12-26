import pygame
import random
from typing import Tuple
from settings import *


class GameObject(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * TILE_SIZE, y * TILE_SIZE)


class Block(GameObject):
    def __init__(self, x: int, y: int, type_block: str):
        color = BROWN if type_block == BLOCK_TYPES["BRICK"] else GRAY
        super().__init__(x, y, color)
        self.type = type_block
        self.hp = 2 if self.type == BLOCK_TYPES["BRICK"] else 999

    def hit(self):
        if self.type == BLOCK_TYPES["BRICK"]:
            self.hp -= 1
            if self.hp == 1:
                # Малюємо "пошкодження"
                pygame.draw.rect(self.image, BLACK, (10, 10, 30, 30))
            if self.hp <= 0:
                self.kill()


class Bullet(GameObject):
    def __init__(self, x, y, direction, owner, damage=1):
        super().__init__(x // TILE_SIZE, y // TILE_SIZE, YELLOW)
        self.image = pygame.Surface((10, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction
        self.speed = 7
        self.owner = owner
        self.damage = damage

    def update(self, walls):
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        if not pygame.display.get_surface().get_rect().contains(self.rect):
            self.kill()
            return

        hit_list = pygame.sprite.spritecollide(self, walls, False)
        if hit_list:
            for wall in hit_list:
                if wall.type == BLOCK_TYPES["BRICK"]:
                    wall.hit()
                self.kill()
                break


class Item(GameObject):
    def __init__(self, x, y, item_type):
        color = RED if item_type == "HEART" else BLUE
        super().__init__(x // TILE_SIZE, y // TILE_SIZE, color)
        self.image = pygame.Surface((20, 20))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.item_type = item_type
        font = pygame.font.SysFont("Arial", 10)
        text = "HP" if item_type == "HEART" else "DMG"
        txt_surf = font.render(text, True, WHITE)
        self.image.blit(txt_surf, (2, 2))


class Tank(GameObject):
    def __init__(self, x, y, color, hp):
        super().__init__(x, y, color)
        self.base_color = color
        self.hp = hp
        self.direction = (0, -1)
        self.last_shot = 0
        self.damage_modifier = 0
        self.render_tank()


    def render_tank(self):
        self.image.fill(self.base_color)
        barrel_color = (230, 230, 0)
        bw, bh = 10, 20

        if self.direction == (0, -1):
            pygame.draw.rect(self.image, barrel_color, (TILE_SIZE // 2 - bw//2, 0, bw, bh))
        elif self.direction == (0, 1):
            pygame.draw.rect(self.image, barrel_color, (TILE_SIZE // 2 - bw//2, TILE_SIZE - bh, bw, bh))
        elif self.direction == (1, 0):
            pygame.draw.rect(self.image, barrel_color, (TILE_SIZE - bh, TILE_SIZE // 2 - bw // 2, bh, bw))
        elif self.direction == (-1, 0):
            pygame.draw.rect(self.image, barrel_color, (0, TILE_SIZE // 2 - bw // 2, bh, bw))


    def move(self, dx, dy, obstacles):
        self.rect.x += dx
        for obj in obstacles:
            if obj != self and self.rect.colliderect(obj.rect):
                if dx > 0:
                    self.rect.right = obj.rect.left
                if dx < 0:
                    self.rect.left = obj.rect.right

        self.rect.y += dy
        for obj in obstacles:
            if obj != self and self.rect.colliderect(obj.rect):
                if dy > 0:
                    self.rect.bottom = obj.rect.top
                if dy < 0:
                    self.rect.top = obj.rect.bottom

        if dx != 0 or dy != 0:
            new_dir = (1 if dx > 0 else -1 if dx < 0 else 0,
                              1 if dy > 0 else -1 if dy < 0 else 0)
            if new_dir != self.direction:
                self.direction = new_dir
                self.render_tank()

    def shoot(self, current_time, bullets_group, tag):
        if current_time - self.last_shot > SHOOT_DELAY:
            bullet = Bullet(self.rect.centerx, self.rect.centery, self.direction, tag, 1 + self.damage_modifier)
            bullets_group.add(bullet)
            self.last_shot = current_time


class Player(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN, PLAYER_HP)
        self.start_pos = (x * TILE_SIZE, y * TILE_SIZE)

    def add_hp(self, amount):
        self.hp += amount
        if self.hp > 3:
            self.hp = 3

    def add_modifier(self):
        self.damage_modifier += 1


class Enemy(Tank):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 2)  # HP ворога = 2
        self.move_timer = 0
        self.move_delay = 1000
        self.current_move = (0, 0)

    def update_ai(self, player, all_obstacles, current_time, bullets_group):
        shoot_chance = 0.01

        if abs(self.rect.x - player.rect.x) < 20 or abs(self.rect.y - player.rect.y) < 20:
            shoot_chance = 0.05

        if random.random() < shoot_chance:
            self.shoot(current_time, bullets_group, "enemy")

        if current_time - self.move_timer > self.move_delay:
            dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            self.current_move = random.choice(dirs)
            self.move_timer = current_time

        prev_pos = self.rect.topleft

        self.move(self.current_move[0] * 2, self.current_move[1] * 2, all_obstacles)

        if self.rect.topleft == prev_pos:
            self.move_timer = 0