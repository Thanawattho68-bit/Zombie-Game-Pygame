import pygame as pg
import random
import os
from base_entity import BaseEntity
from settings import *
from wave_difficulty import WaveDifficulty
from utils import get_random_image

class Zombie(BaseEntity):
    def __init__(self, x, y, hp, speed, entity, attack_damage, sound_folder, size=(35, 35)):
        super().__init__(x, y, hp, speed, entity, size=size)
        self.attack_damage = attack_damage
        self.pos = pg.math.Vector2(x, y)
        self._load_sounds(sound_folder, ZOMBIE_VOLUME, ["idle", "death", "damage"])

    def spawn(self):
        pass

    def play_sound(self, sound_type):
        super().play_sound(sound_type) # เรียกใช้จากเบสเอนทิตี้

    def update(self, *args, **kwargs):
        player_pos = kwargs.get('player_pos')
        
        if player_pos:
            target_vector = pg.math.Vector2(player_pos)
            current_vector = pg.math.Vector2(self.pos)
            
            direction = target_vector - current_vector
            
            if direction.length() > 0:
                direction = direction.normalize() * self.speed
                self.pos += direction
                self.rect.center = (self.pos.x, self.pos.y)

        # จัดการเสียง Idle โดยใช้เบสเอนทิตี้
        self.handle_idle_sound(3000, 10000)

    def attack(self, target=None):
        if target and self.rect.colliderect(target.rect):
            target.take_damage(self.attack_damage)

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

# --- Factory (โรงงานสร้างซอมบี้) ---

class ZombieFactory:
    def __init__(self, difficulty_strategy: WaveDifficulty):
        self.strategy = difficulty_strategy

    def _get_random_spawn_pos(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        margin = 100 # ให้เกิดนอกจอเล็กน้อย

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
