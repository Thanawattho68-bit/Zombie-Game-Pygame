import pygame as pg
import random
from abc import abstractmethod, ABC
from settings import *

class BaseEntity(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, entity, size=(35, 35)):
        super().__init__()
        # พยายามโหลดรูปภาพ ถ้าไม่มีหรือโหลดไม่ได้จะสร้าง Surface สีพื้นแทน (ตามความต้องการของผู้ใช้)
        success = False
        if entity:
            try:
                self.image = pg.image.load(entity).convert_alpha()
                self.image = pg.transform.scale(self.image, size)
                success = True
            except Exception as e:
                print(f"Warning: Could not load entity image '{entity}' - {e}")
        
        if not success:
            # สร้างสีพื้นแบบสุ่มเล็กน้อยเพื่อให้แยกแยะตัวที่ไม่มีรูปได้
            self.image = pg.Surface(size)
            placeholder_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
            self.image.fill(placeholder_color)
            # วาดกรอบให้ดูเป็นบล็อก
            pg.draw.rect(self.image, WHITE, self.image.get_rect(), 2)

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
    def play_sound(self, sound_type):
        pass

    @abstractmethod
    def attack(self, target=None):
        pass

    def take_damage(self, damage):
        self.hp -= damage
        self.play_sound("damage")
        if self.hp <= 0:
            self.play_sound("death")
            self.kill()
            return True
        return False