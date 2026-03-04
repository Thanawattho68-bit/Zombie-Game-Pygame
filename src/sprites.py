import pygame as pg
import math
from settings import *

class Player(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # TODO: โหลดรูปภาพตัวละคร (assets/sprites/player.png)
        self.image = pg.Surface((40, 40))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.hp = PLAYER_HP
        self.speed = PLAYER_SPEED

    def update(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.rect.x -= self.speed
        if keys[pg.K_d]: self.rect.x += self.speed
        if keys[pg.K_w]: self.rect.y -= self.speed
        if keys[pg.K_s]: self.rect.y += self.speed

        # ป้องกันไม่ให้ตัวละครออกนอกหน้าจอ
        self.rect.clamp_ip(pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

class Bullet(pg.sprite.Sprite):
    def __init__(self, x, y, dx, dy):
        super().__init__()
        self.image = pg.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        # ลบกระสุนถ้าออกนอกหน้าจอ
        if not pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT).colliderect(self.rect):
            self.kill()

class Zombie(pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, color):
        super().__init__()
        self.image = pg.Surface((35, 35))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.hp = hp
        self.speed = speed

# --- ประเภทย่อยของซอมบี้ ---

class NormalZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, ZOMBIE_NORMAL_HP, ZOMBIE_NORMAL_SPEED, RED)

class FastZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, ZOMBIE_FAST_HP, ZOMBIE_FAST_SPEED, (255, 128, 0)) # ส้ม

class TankZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, ZOMBIE_TANK_HP, ZOMBIE_TANK_SPEED, (139, 0, 0)) # แดงเข้ม
        self.image = pg.Surface((55, 55)) # ตัวใหญ่ขึ้น
        self.image.fill((139, 0, 0))
        self.rect = self.image.get_rect(center=(x, y))
