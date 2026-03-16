import pygame as pg
import math
from abc import ABC, abstractmethod
from settings import *
from utils import load_image

#composition ให้ weapon เก็บ bullet
class Bullet(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, image_path):
        super().__init__()
        # ใช้ utility ในการโหลดรูปภาพ (DRY)
        self.image = load_image(image_path, (20, 20), fallback_color=RED)
            
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