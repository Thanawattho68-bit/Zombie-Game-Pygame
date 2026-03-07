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
        self.sound_folder = sound_folder
        self._load_sounds()

    def _load_sounds(self):
        # โหลดเสียงโดยใช้ prefix
        self.sounds = {"damage": [], "death": [], "reload": []}
        if not os.path.exists(self.sound_folder):
            # ไม่ต้องปริ้น Warning รัวๆ ถ้าโฟลเดอร์ไม่มี แค่ข้ามไปพอ
            return
            
        for f in os.listdir(self.sound_folder):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                for s_type in self.sounds.keys():
                    if f.startswith(s_type):
                        try:
                            snd = pg.mixer.Sound(os.path.join(self.sound_folder, f))
                            self.sounds[s_type].append(snd)
                        except Exception as e:
                            print(f"Warning: Could not load player sound '{f}': {e}")

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def play_sound(self, sound_type):
        if hasattr(self, 'sounds') and sound_type in self.sounds and self.sounds[sound_type]:
            random.choice(self.sounds[sound_type]).play()

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

    def attack(self, target=None):
        return self.weapon.pull_trigger()

class Soldier(Player):
    def __init__(self, x, y):
        folder = "assets/character/player/Soldier"
        super().__init__(x, y, 120, 5, f"{folder}/image", f"{folder}/sound", weapon_class=M16)
        self.char_name = "Soldier"

class Scout(Player):
    def __init__(self, x, y):
        folder = "assets/character/player/Scout"
        super().__init__(x, y, 80, 7, f"{folder}/image", f"{folder}/sound", weapon_class=M16)
        self.char_name = "Scout"

class Defender(Player):
    def __init__(self, x, y):
        folder = "assets/character/player/Defender"
        super().__init__(x, y, 200, 3.5, f"{folder}/image", f"{folder}/sound", weapon_class=M16)
        self.char_name = "Defender"

class Naoya(Player):
    def __init__(self, x, y):
        folder = "assets/character/player/Naoya"
        super().__init__(x, y, 50, 50, f"{folder}/image", f"{folder}/sound", weapon_class=M16)
        self.char_name = "Naoya"
