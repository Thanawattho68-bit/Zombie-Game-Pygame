import pygame as pg
import random
from base_entity import CombatEntity
from settings import *
from weapons import Glock, M16
from utils import get_random_image
from sound_component import SoundComponent

class Player(CombatEntity):
    def __init__(self, x, y, hp, speed, image_folder, sound_folder, weapon_class=Glock):
        img = get_random_image(image_folder)
        super().__init__(x, y, hp, speed, img, size=(50, 50))
        
        self.weapon = weapon_class(x, y) 
        self.sound = SoundComponent(self, sound_folder, PLAYER_VOLUME, ["damage", "death", "reload", "idle", "narrate"])
        self.next_idle_sound_time = 0
        self.next_narrate_time = 0

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def reload_weapon(self):
        if self.weapon.reload():
            self.sound.play("reload")

    def handle_idle_sounds(self):
        now = pg.time.get_ticks()
        # Idle
        if self.next_idle_sound_time == 0 or now >= self.next_idle_sound_time:
             self.sound.play("idle")
             self.next_idle_sound_time = now + random.randint(10000, 20000)
        
        # Narrate
        if not self.sound.narrate_played:
            if self.next_narrate_time == 0:
                self.next_narrate_time = now + random.randint(10000, 60000)
            if now >= self.next_narrate_time:
                self.sound.play("narrate")

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
        self.handle_idle_sounds()

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
