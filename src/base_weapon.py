import pygame as pg
import math
from settings import *
from base_bullet import NineMM, FiveFiveSix

class BaseWeapon(pg.sprite.Sprite):
    def __init__(self, x, y, weapon, bullet_type, magazine_size, reload_time, fire_rate, size=(40, 15)):
        super().__init__()
        try:
            self.original_image = pg.image.load(weapon).convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, size)
        except Exception as e:
            print(f"Warning: Could not load weapon image '{weapon}' - {e}")
            self.original_image = pg.Surface(size)
            self.original_image.fill(DARK_GRAY)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_type = bullet_type
        self.magazine_size = magazine_size
        self.current_ammo = magazine_size
        self.reload_time = reload_time
        self.fire_rate = fire_rate * 1000
        self.last_shot_time = 0
        self.angle = 0

    def update(self, *args, **kwargs):
        player_pos = kwargs.get('player_pos', self.rect.center)
        if hasattr(self, 'owner_center'):
            # In case it's directly assigned instead
            pass
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
    def __init__(self, x, y):
        # เราขอแค่ x, y เพื่อรู้ว่าจะให้ปืนเกิดตรงไหน
        # ส่วนค่าอื่นๆ เรา (Glock) รู้ดีอยู่แล้วว่าเราคืออะไร
        super().__init__(
            x, y, 
            "assets/weapon/glock/glock.png",  # weapon
            NineMM,                           # bullet_type
            10,                               # magazine_size
            1,                                # reload_time
            0.1,                              # fire_rate
            size=(30, 15)                     # ขนาดปืนพก
        )

class M16(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/m16/m16.png", 
            FiveFiveSix, 
            30, 
            2, 
            0.1,
            size=(60, 20) # ขนาดปืนไรเฟิลจะยาวกว่าปกติ
        )
