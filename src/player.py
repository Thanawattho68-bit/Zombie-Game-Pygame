import pygame as pg
import random
from base_entity import BaseEntity
from settings import *
from weapons import Glock, M16
from utils import get_random_image
from sound_component import SoundComponent

class Player(BaseEntity):
    def __init__(self, x, y, hp, speed, image_folder, sound_folder, weapon_class=Glock):
        img = get_random_image(image_folder)
        super().__init__(x, y, hp, speed, img, size=(50, 50))
        
        self.weapon = weapon_class(x, y) 
        self.sound = SoundComponent(self, sound_folder, PLAYER_VOLUME, ["damage", "death", "reload", "idle"])

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def reload_weapon(self):
        if self.weapon.reload():
            self.sound.play("reload")

    def take_damage(self, damage):
        self.hp -= damage
        if self.sound:
            self.sound.play("damage")
        
        if self.hp <= 0:
            # ถ้าเป็น Player ตาย ให้หยุดเสียงทุกอย่างในเกม (ยกเว้นเพลงถ้าต้องการ แต่ pg.mixer.stop() จะหยุด SFX ทั้งหมด)
            # เราหยุดก่อนที่จะเริ่มเล่นเสียง Death ของตัวเอง เพื่อให้เสียง Death ไม่โดนหยุดไปด้วย
            pg.mixer.stop()
            if self.sound:
                self.sound.play("death")
            self.kill()
            return True
        return False


    def update(self, *args, **kwargs):
        keys = pg.key.get_pressed()
        direction = pg.math.Vector2(0, 0)

        if keys[WALK_LEFT]: direction.x -= 1
        if keys[WALK_RIGHT]: direction.x += 1
        if keys[WALK_UP]: direction.y -= 1
        if keys[WALK_DOWN]: direction.y += 1

        if direction.length() > 0:
            direction = direction.normalize() * self.speed
            self.rect.centerx += int(direction.x)
            self.rect.centery += int(direction.y)

        self.rect.clamp_ip(pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.weapon.update(self.rect.center)
        super().handle_idle_sounds(10000, 20000)

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
