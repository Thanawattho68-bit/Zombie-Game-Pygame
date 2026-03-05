import pygame as pg
from abc import ABC, abstractmethod
from settings import *

#composition ให้ weapon เก็บ bullet
class Bullet(ABC,pg.sprite.Sprite):
    def __init__(self, x, y, speed, bullet):
        super().__init__()
        try:
            self.image = pg.image.load(bullet).convert_alpha()
        except pg.error as e:
            print(f"Error loading image: {e}")
            self.image = pg.Surface((10, 10))
            self.image.fill(DARK_GRAY)
        self.rect = self.image.get_rect(center=(x, y))

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def hit(self, target):
        pass