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
        self.next_idle_sound_time = 0

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def handle_idle_sounds(self, min_delay, max_delay):
        if not self.sound: return
        now = pg.time.get_ticks()
        if self.next_idle_sound_time == 0:
            self.next_idle_sound_time = now + random.randint(5000, 10000)
            
        if now >= self.next_idle_sound_time:
             self.sound.play("idle")
             self.next_idle_sound_time = now + random.randint(min_delay, max_delay)

    @abstractmethod
    def attack(self, target=None):
        """กำหนดให้ Entity ทุกตัวในเกมต้องมีเมธอดโจมตี"""
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