import pygame as pg
from abc import abstractmethod, ABC
from settings import *

class BaseEntity(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, entity):
        super().__init__()
        try:
            self.image = pg.image.load(entity).convert_alpha()
        except pg.error as e:
            print(f"Error loading image: {e}")
            self.image = pg.Surface((35, 35))
            self.image.fill(GREEN)

        self.hp = hp
        self.speed = speed
        self.rect = self.image.get_rect(center=(x, y)) # เอา center ของ entity ไปไว้ที่ x, y
    
    @abstractmethod
    def spawn(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def attack(self, target):
        pass

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False