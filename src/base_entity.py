import pygame as pg
from abc import abstractmethod, ABC
from settings import *
from sound_component import SoundComponent
from utils import load_image

class BaseEntity(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, image_path, size=(35, 35)):
        super().__init__()
        # ใช้ utility ในการโหลดรูปภาพเพื่อลดความซ้ำซ้อนของโค้ด (DRY)
        self.image = load_image(image_path, size)
        self.hp = hp
        self.speed = speed
        self.rect = self.image.get_rect(center=(x, y))
        self.sound = None # จะถูกสร้างโดยคลาสลูกถ้าต้องการใช้เสียง

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def take_damage(self, damage):
        self.hp -= damage
        if self.sound:
            self.sound.play("damage")
        
        if self.hp <= 0:
            if self.sound:
                self.sound.play("death")
            self.kill()
            return True
        return False

class CombatEntity(BaseEntity):
    """Subclass สำหรับ Entity ที่สามารถโจมตีได้ (ISP)"""
    @abstractmethod
    def attack(self, target=None):
        pass