import pygame
import sys
import random
import time
from settings import *
from utils import ensure_level_files, load_level_matrix, save_highscore, load_highscore
from models import Block, Player, Enemy, Item

class Game:
    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 20)
        self.large_font = pygame.font.SysFont("Arial", 40)
        self.clock = pygame.time.Clock()
        self.running = True

        self.level = 1
        self.score = 0
        self.game_state = "MENU"

        self.total_game_time = 0
        self.start_level_time = 0

        ensure_level_files()
        self.best_time = load_highscore()
        config = LEVEL_CONFIG[1]
        self.screen_width = config["size"] * TILE_SIZE
        self.screen_height = config["size"] * TILE_SIZE + 40
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Battle City Remake")

    def init_level(self):
        config = LEVEL_CONFIG.get(self.level)
        if not config:
            self.game_state = "WIN"
            return

        self.all_sprites = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.items = pygame.sprite.Group()

        matrix = load_level_matrix(self.level)
        player_spawn = (1, 1)

        for r, row in enumerate(matrix):
            for c, char in enumerate(row):
                if char in [BLOCK_TYPES["BRICK"], BLOCK_TYPES["STEEL"]]:
                    wall = Block(c, r, char)
                    self.walls.add(wall)
                    self.all_sprites.add(wall)
                elif char == BLOCK_TYPES["PLAYER"]:
                    player_spawn = (c, r)

        self.player = Player(player_spawn[0], player_spawn[1])
        self.all_sprites.add(self.player)

        enemy_count = config["enemies"]
        attempts = 0

        while len(self.enemies) < enemy_count and attempts < 200:
            ex, ey = random.randint(1, config["size"] - 2), random.randint(1, config["size"] - 2)

            if matrix[ey][ex] == BLOCK_TYPES["EMPTY"]:
                dist = abs(ex - player_spawn[0]) + abs(ey - player_spawn[1])
                if dist > 4:
                    temp_enemy = Enemy(ex, ey)
                    if not pygame.sprite.spritecollideany(temp_enemy, self.enemies):
                        self.enemies.add(temp_enemy)
                        self.all_sprites.add(temp_enemy)
            attempts += 1

        self.start_level_time = time.time()

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -PLAYER_SPEED
        if keys[pygame.K_RIGHT]: dx = PLAYER_SPEED
        if keys[pygame.K_UP]: dy = -PLAYER_SPEED
        if keys[pygame.K_DOWN]: dy = PLAYER_SPEED

        if dx != 0 or dy != 0:
            obstacles = self.walls.sprites() + self.enemies.sprites()
            self.player.move(dx, dy, obstacles)

        if keys[pygame.K_SPACE]:
            self.player.shoot(pygame.time.get_ticks(), self.bullets, "player")

    def spawn_item(self, x, y):
        chance = random.random()
        if chance < 0.30:
            item = Item(x, y, "HEART")
            self.items.add(item)
            self.all_sprites.add(item)
        elif chance < 0.50:
            item = Item(x, y, "SWORD")
            self.items.add(item)
            self.all_sprites.add(item)

    def update(self):
        current_time_ms = pygame.time.get_ticks()
        all_obstacles = self.walls.sprites() + [self.player] + self.enemies.sprites()

        for enemy in self.enemies:
            enemy.update_ai(self.player, all_obstacles, current_time_ms, self.bullets)

        for bullet in self.bullets:
            bullet.update(self.walls)

            if bullet.owner == "player":
                hits = pygame.sprite.spritecollide(bullet, self.enemies, False)
                if hits:
                    enemy = hits[0]
                    enemy.hp -= bullet.damage
                    bullet.kill()
                    if enemy.hp <= 0:
                        self.score += 100
                        self.spawn_item(enemy.rect.centerx, enemy.rect.centery)
                        enemy.kill()

            elif bullet.owner == "enemy":
                if pygame.sprite.collide_rect(bullet, self.player):
                    self.player.hp -= 1
                    bullet.kill()
                    if self.player.hp <= 0:
                        self.game_state = "GAME_OVER"

        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            if item.item_type == "HEART":
                self.player.add_hp(1)
                self.score += 50
            elif item.item_type == "SWORD":
                self.player.add_modifier()
                self.score += 75

        if len(self.enemies) == 0:
            level_duration = time.time() - self.start_level_time
            self.total_game_time += level_duration

            if self.level == 3:
                save_highscore(self.total_game_time)
                self.game_state = "WIN"
            else:
                self.game_state = "LEVEL_COMPLETE"

    def draw_ui(self):
        pygame.draw.rect(self.screen, GRAY, (0, self.screen_height - 40, self.screen_width, 40))

        hp_label = self.font.render("Lives:", True, WHITE)
        self.screen.blit(hp_label, (10, self.screen_height - 35))

        for i in range(self.player.hp):
            x_pos = 70 + i * 25
            y_pos = self.screen_height - 20
            pygame.draw.circle(self.screen, RED, (x_pos, y_pos), 8)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)

        current_level_time = 0
        if self.game_state == "PLAYING":
            current_level_time = time.time() - self.start_level_time

        total = self.total_game_time + current_level_time
        time_text = self.font.render(f"Time: {int(total)}s", True, WHITE)

        self.screen.blit(score_text, (200, self.screen_height - 35))
        self.screen.blit(level_text, (350, self.screen_height - 35))
        self.screen.blit(time_text, (450, self.screen_height - 35))

    def draw_menu(self, title, subtitle, show_stats=False):
        self.screen.fill(BLACK)

        title_surf = self.large_font.render(title, True, YELLOW)
        rect = title_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 60))
        self.screen.blit(title_surf, rect)

        sub_surf = self.font.render(subtitle, True, WHITE)
        rect2 = sub_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
        self.screen.blit(sub_surf, rect2)

        if show_stats:
            info_surf = self.font.render(f"Score: {self.score} | Time: {self.total_game_time:.2f}s", True, GREEN)
            rect3 = info_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 40))
            self.screen.blit(info_surf, rect3)

            if self.game_state == "WIN" and self.best_time < 9000:
                best_surf = self.font.render(f"Best Record: {self.best_time:.2f}s", True, GRAY)
                rect4 = best_surf.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 70))
                self.screen.blit(best_surf, rect4)

        pygame.display.flip()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.game_state == "MENU":
                            self.level = 1
                            self.score = 0
                            self.total_game_time = 0
                            self.init_level()
                            self.game_state = "PLAYING"

                        elif self.game_state in ["GAME_OVER", "WIN"]:
                            self.game_state = "MENU"

                        elif self.game_state == "LEVEL_COMPLETE":
                            self.level += 1
                            self.init_level()
                            self.game_state = "PLAYING"

            if self.game_state == "PLAYING":
                self.handle_input()
                self.update()
                self.screen.fill(BLACK)
                self.all_sprites.draw(self.screen)
                self.bullets.draw(self.screen)
                self.draw_ui()
                pygame.display.flip()

            elif self.game_state == "LEVEL_COMPLETE":
                self.draw_menu(f"LEVEL {self.level} CLEARED", "Press ENTER for next level", show_stats=True)

            elif self.game_state == "GAME_OVER":
                self.draw_menu("GAME OVER", "Press ENTER to main menu")

            elif self.game_state == "WIN":
                self.draw_menu("VICTORY!", "Press ENTER", show_stats=True)

            elif self.game_state == "MENU":
                self.draw_menu("BATTLE CITY", "Press ENTER to start")

            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()