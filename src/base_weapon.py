import pygame as pg
import math
from abc import ABC, abstractmethod
from settings import *

#composition ให้ Player เก็บ weapon
class BaseWeapon(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, speed, weapon):
        super().__init__()
        try:
            self.original_image = pg.image.load(weapon).convert_alpha()
        except pg.error as e:
            print(f"Error loading image: {e}")
            self.original_image = pg.Surface((10, 10))
            self.original_image.fill(DARK_GRAY)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed


    def rotate_to_mouse(self):
        mx, my = pg.mouse.get_pos()
        #คำนวณความต่างของพิกัด
        dx = mx - self.rect.centerx
        dy = my - self.rect.centery
        #คำนวณมุม (ในทางคณิตศาสตร์แกน y ของ Pygame จะกลับด้าน เลยต้องติดลบที่ dy)
        self.angle = math.degrees(math.atan2(-dy, dx))
        
        #หมุนภาพต้นฉบับตามมุมที่ได้
        self.image = pg.transform.rotate(self.original_image, self.angle)
        #อัปเดตกรอบ (rect) ให้จุดกึ่งกลางอยู่ที่เดิม (เพราะการหมุนทำให้ขนาดสี่เหลี่ยมเปลี่ยน)
        self.rect = self.image.get_rect(center=self.rect.center)


    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def shoot(self, target):
        pass