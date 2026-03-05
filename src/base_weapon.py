import pygame as pg
import math
import settings
from base_bullet import NineMM, FiveFiveSix

class BaseWeapon(pg.sprite.Sprite):
    def __init__(self, x, y, weapon_type, bullet_type, magazine_size, reload_time, fire_rate):
        super().__init__()
        try:
            self.original_image = pg.image.load(weapon_type).convert_alpha()
        except:
            self.original_image = pg.Surface((10, 10))
            self.original_image.fill(DARK_GRAY)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_type = bullet_type
        self.magazine_size = magazine_size
        self.current_ammo = magazine_size
        self.reload_time = reload_time
        self.fire_rate = fire_rate * 1000
        self.last_shot_time = 0

    def update(self, player_pos):
        self.rect.center = player_pos
        self.rotate_to_mouse()

    def rotate_to_mouse(self):
        mx, my = pg.mouse.get_pos()
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        self.angle = math.degrees(math.atan2(-dy, dx))
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        direction = pg.math.Vector2(1, 0).rotate(-self.angle)
        return self.bullet_type(self.rect.centerx, self.rect.centery, direction)

    def pull_trigger(self):
        now = pg.time.get_ticks() # ต้องดึงเวลาปัจจุบันมาด้วย
        if self.current_ammo > 0 and now - self.last_shot_time > self.fire_rate:
            # ต้องเช็คด้วยว่า เวลาผ่านไปนานพอหรือยัง (now - last_shot > delay)
            self.current_ammo -= 1
            self.last_shot_time = now
            return self.shoot()

    def reload(self):
        if self.current_ammo < self.magazine_size:
            self.current_ammo = self.magazine_size

class Glock(BaseWeapon):
    def __init__(self, x, y, weapon_type, bullet_type, magazine_size, reload_time, fire_rate):
        super().__init__(x, y, "assets/weapon/glock/glock.png", NineMM, 10, 1, 0.1)

class M16(BaseWeapon):
    def __init__(self, x, y, weapon_type, bullet_type, magazine_size, reload_time, fire_rate)
        super().__init__(x, y, "assets/weapon/m16/m16.png", FiveFiveSix, 30, 2, 0.1)