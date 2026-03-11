import pygame as pg
import math
from abc import ABC, abstractmethod
from settings import *

#composition ให้ weapon เก็บ bullet
class Bullet(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, image_path):
        super().__init__()
        try:
            self.image = pg.image.load(image_path).convert_alpha()
            # ปรับขนาดกระสุนให้สมส่วนขึ้น (เช่น ยาว 15 กว้าง 5 หรือตามต้องการ)
            self.image = pg.transform.scale(self.image, (20, 20))
        except Exception as e:
            print(f"Warning: Could not load bullet image '{image_path}' - {e}")
            self.image = pg.Surface((10,5))
            self.image.fill(RED)
            
        # หมุนภาพให้หันไปตามทิศทาง (direction)
        # เนื่องจาก Pygame rotate หมุนทวนเข็มนาฬิกา และแกน Y เป็นบวกเมื่อลงล่าง
        angle = math.degrees(math.atan2(-direction.y, direction.x))
        self.image = pg.transform.rotate(self.image, angle)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pg.math.Vector2(x, y)
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def update(self, *args, **kwargs):
        self.pos += self.direction * self.speed
        self.rect.center = (self.pos.x, self.pos.y)
        if not pg.display.get_surface().get_rect().contains(self.rect):
            self.kill()

    def hit(self, target):
        target.take_damage(self.damage)
        self.kill()

class NineMM(Bullet):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, 20, 35, "assets/weapon/glock/image/nine_mm.png")

class FiveFiveSix(Bullet):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, 60, 45, "assets/weapon/m16/image/five_five_six.png")