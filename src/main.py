import pygame as pg
import random
import math
from settings import *
from sprites import Player, Bullet, NormalZombie, FastZombie, TankZombie

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Zombie Survival - Mini Project")
        self.clock = pg.time.Clock()
        self.new_game()

    def new_game(self):
        # กลุ่ม Sprite
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()

        # ผู้เล่น
        self.player = Player()
        self.all_sprites.add(self.player)

        # ข้อมูลเกม
        self.score = 0
        self.wave = 1
        self.spawn_wave()

    def spawn_wave(self):
        # สุ่มซอมบี้ตามจำนวน Wave
        num_zombies = self.wave * 2
        for i in range(num_zombies):
            # สุ่มตำแหน่งขอบหน้าจอ
            edge = random.choice(['top', 'bottom', 'left', 'right'])
            if edge == 'top': x, y = random.randint(0, SCREEN_WIDTH), -50
            elif edge == 'bottom': x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50
            elif edge == 'left': x, y = -50, random.randint(0, SCREEN_HEIGHT)
            else: x, y = SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)

            # สุ่มประเภทซอมบี้
            rand_val = random.random()
            if rand_val < 0.1 and self.wave >= 3: zombie = TankZombie(x, y)
            elif rand_val < 0.3 and self.wave >= 2: zombie = FastZombie(x, y)
            else: zombie = NormalZombie(x, y)

            self.all_sprites.add(zombie)
            self.zombies.add(zombie)

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.playing = False
                pg.quit()
                exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1: # คลิกซ้ายเพื่อยิง
                    self.shoot()

    def shoot(self):
        # ทิศทางยิงไปที่เมาส์
        mx, my = pg.mouse.get_pos()
        dx, dy = mx - self.player.rect.centerx, my - self.player.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx, dy = dx / dist, dy / dist
            bullet = Bullet(self.player.rect.centerx, self.player.rect.centery, dx, dy)
            self.all_sprites.add(bullet)
            self.bullets.add(bullet)

    def update(self):
        # อัปเดตทุก Sprite
        self.all_sprites.update()
        for zombie in self.zombies:
            zombie.update(self.player.rect)

        # การเชนพุ่งชน (Collision)
        # Bullet ชน Zombie
        hits = pg.sprite.groupcollide(self.zombies, self.bullets, False, True)
        for zombie, bullets in hits.items():
            zombie.hp -= 10
            if zombie.hp <= 0:
                zombie.kill()
                self.score += 10

        # Zombie ชน Player
        if pg.sprite.spritecollide(self.player, self.zombies, False):
            print("Game Over!! คะแนนที่ได้:", self.score)
            self.playing = False

        # จบ Wave เมื่อซอมบี้ตายหมด
        if len(self.zombies) == 0:
            self.wave += 1
            self.spawn_wave()

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.all_sprites.draw(self.screen)

        # วาดข้อความ (Score & Wave)
        font = pg.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        wave_text = font.render(f"Wave: {self.wave}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(wave_text, (10, 40))

        pg.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
