import pygame as pg
from abc import abstractmethod, ABC
from settings import *

class BaseEntity(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, entity, size=(35, 35)):
        super().__init__()
        try:
            self.image = pg.image.load(entity).convert_alpha()
            self.image = pg.transform.scale(self.image, size)
        except Exception as e:
            print(f"Warning: Could not load entity image '{entity}' - {e}")
            self.image = pg.Surface(size)
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
    def attack(self, target=None):
        pass

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()
            return True
        return False