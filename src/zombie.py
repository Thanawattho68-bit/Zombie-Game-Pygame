import pygame as pg
import random
from base_entity import BaseEntity
from settings import *
from wave_difficulty import WaveDifficulty
from utils import get_random_image, get_direction_vector
from sound_component import SoundComponent

class Zombie(BaseEntity):
    def __init__(self, x, y, hp, speed, entity_img, attack_damage, sound_folder, size=(35, 35)):
        super().__init__(x, y, hp, speed, entity_img, size=size)
        self.attack_damage = attack_damage
        self.pos = pg.math.Vector2(x, y)
        self.sound = SoundComponent(self, sound_folder, ZOMBIE_VOLUME, ["idle", "death", "damage"])
        self.next_idle_sound_time = 0

    def handle_idle_sounds(self):
        now = pg.time.get_ticks()
        if self.next_idle_sound_time == 0 or now >= self.next_idle_sound_time:
             self.sound.play("idle")
             self.next_idle_sound_time = now + random.randint(3000, 10000)

    def update(self, *args, **kwargs):
        player_pos = kwargs.get('player_pos')
        if player_pos:
            direction = get_direction_vector(self.pos, player_pos)
            if direction.length() > 0:
                self.pos += direction * self.speed
                self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.handle_idle_sounds()

    def attack(self, target=None):
        if target and self.rect.colliderect(target.rect):
            target.take_damage(self.attack_damage)
            return True
        return False

# --- Zombie Subclasses ---

class NormalZombie(Zombie):
    def __init__(self, x, y):
        folder = "assets/character/zombie/zombie_normal"
        img = get_random_image(f"{folder}/image")
        super().__init__(x, y, 50, 2.5, img, 10, f"{folder}/sound")

class FastZombie(Zombie):
    def __init__(self, x, y):
        folder = "assets/character/zombie/zombie_fast"
        img = get_random_image(f"{folder}/image")
        super().__init__(x, y, 250, 6, img, 15, f"{folder}/sound")

class TankZombie(Zombie):
    def __init__(self, x, y):
        folder = "assets/character/zombie/zombie_tank"
        img = get_random_image(f"{folder}/image")
        super().__init__(x, y, 4000, 3.5, img, 24, f"{folder}/sound", size=(80, 80))

# --- Factory ---

class ZombieFactory:
    def __init__(self, difficulty_strategy: WaveDifficulty):
        self.strategy = difficulty_strategy

    def _get_random_spawn_pos(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        margin = 100 

        if side == 'top':
            return random.randint(0, SCREEN_WIDTH), -margin
        elif side == 'bottom':
            return random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + margin
        elif side == 'left':
            return -margin, random.randint(0, SCREEN_HEIGHT)
        else: # right
            return SCREEN_WIDTH + margin, random.randint(0, SCREEN_HEIGHT)

    def spawn_wave(self, wave_num):
        config = self.strategy.get_spawn_config(wave_num)
        
        if config is None:
            return None 

        new_zombies = []
        zombie_classes = {
            "normal": NormalZombie,
            "fast": FastZombie,
            "tank": TankZombie
        }

        for z_type, count in config.items():
            if z_type in zombie_classes:
                for _ in range(count):
                    x, y = self._get_random_spawn_pos()
                    zombie_obj = zombie_classes[z_type](x, y)
                    new_zombies.append(zombie_obj)
        
        return new_zombies
