import pygame as pg
from abc import ABC, abstractmethod
from settings import *

#composition ให้ weapon เก็บ bullet
class Bullet(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, direction, speed, damage, image_path):
        super().__init__()
        try:
            self.image = pg.image.load(image_path).convert_alpha()
            self.image = pg.transform.scale(self.image, (10, 10))
        except Exception as e:
            print(f"Warning: Could not load bullet image '{image_path}' - {e}")
            self.image = pg.Surface((10, 10))
            self.image.fill(RED)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pg.math.Vector2(x, y)
        self.direction = direction
        self.speed = speed
        self.damage = damage

    def update(self, *args, **kwargs):
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        if not pg.display.get_surface().get_rect().contains(self.rect):
            self.kill()

    def hit(self, target):
        target.take_damage(self.damage)
        self.kill()

class NineMM(Bullet):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, 20, 35, "assets/bullet/nine_mm/nine_mm.png")

class FiveFiveSix(Bullet):
    def __init__(self, x, y, direction):
        super().__init__(x, y, direction, 30, 45, "assets/bullet/five_five_six/five_five_six.png")