import pygame as pg
import random
import os
from base_entity import BaseEntity
from settings import *
from base_weapon import Glock, M16
from utils import get_random_image

class Player(BaseEntity):
    def __init__(self, x, y, hp, speed, image_folder, sound_folder, weapon_class=Glock):
        # สุ่มรูปภาพจากโฟลเดอร์เฉพาะของคลาสนั้นๆ
        img = get_random_image(image_folder)
        
        # ให้ตัวละคร Player ใหญ่เป็นพิเศษ เช่น 50x50
        # ถ้า img เป็น None คลาส BaseEntity จะจัดการสร้าง Surface สีพื้นให้เองใน try-except
        super().__init__(x, y, hp, speed, img, size=(50, 50))
        
        self.weapon = weapon_class(x, y) 
        self._load_sounds(sound_folder, PLAYER_VOLUME, ["damage", "death", "reload", "idle", "narrate"])

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def play_sound(self, sound_type):
        if sound_type == "death":
            # ถ้าเป็น Player ตาย ให้หยุดเสียงทุกอย่างในเกมทันที (World Stop)
            pg.mixer.stop()
        super().play_sound(sound_type)

    def reload_weapon(self):
        if self.weapon.reload():
            self.play_sound("reload")

    def update(self, *args, **kwargs):
        keys = pg.key.get_pressed()
        direction = pg.math.Vector2(0, 0)

        if keys[WALK_LEFT]: direction.x -= 1
        if keys[WALK_RIGHT]: direction.x += 1
        if keys[WALK_UP]: direction.y -= 1
        if keys[WALK_DOWN]: direction.y += 1

        # ป้องกันการเดินเฉียงแล้วเร็วเกินไป (Normalize)
        if direction.length() > 0:
            direction = direction.normalize() * self.speed
            self.rect.centerx += int(direction.x)
            self.rect.centery += int(direction.y)

        self.rect.clamp_ip(pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.weapon.update(self.rect.center)

        # จัดการเสียง Idle (Player พูด) โดยใช้เบสเอนทิตี้
        self.handle_idle_sound(10000, 20000)
        # จัดการเสียง Narrate (สุ่มพูดภายใน 10-60 วินาทีแรกของแมตช์)
        self.handle_narrate_sound(10000, 60000)

    def attack(self, target=None):
        return self.weapon.pull_trigger()

class Soldier(Player):
    BASE_PATH = "assets/character/player/Soldier"
    def __init__(self, x, y):
        super().__init__(x, y, 120, 5, f"{self.BASE_PATH}/image", f"{self.BASE_PATH}/sound", weapon_class=M16)
        self.char_name = "Soldier"

class Scout(Player):
    BASE_PATH = "assets/character/player/Scout"
    def __init__(self, x, y):
        super().__init__(x, y, 80, 7, f"{self.BASE_PATH}/image", f"{self.BASE_PATH}/sound", weapon_class=M16)
        self.char_name = "Scout"

class Defender(Player):
    BASE_PATH = "assets/character/player/Defender"
    def __init__(self, x, y):
        super().__init__(x, y, 200, 3.5, f"{self.BASE_PATH}/image", f"{self.BASE_PATH}/sound", weapon_class=M16)
        self.char_name = "Defender"

class Naoya(Player):
    BASE_PATH = "assets/character/player/Naoya"
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50, f"{self.BASE_PATH}/image", f"{self.BASE_PATH}/sound", weapon_class=M16)
        self.char_name = "Naoya"
