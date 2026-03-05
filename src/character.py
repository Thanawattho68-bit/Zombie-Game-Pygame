import pygame as pg
import random
from base_entity import BaseEntity
from settings import *
from wave_difficulty import WaveDifficulty
from base_weapon import Glock, M16

# --- 2. ส่วนของ Entities (ตัวละคร) ---

class Player(BaseEntity):
    def __init__(self, x, y, hp, speed, entity):
        # ให้ตัวละคร Player ใหญ่เป็นพิเศษ เช่น 50x50
        super().__init__(x, y, hp, speed, entity, size=(50, 50))
        self.weapon = Glock(x, y) # Default weapon

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

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


class Zombie(BaseEntity):
    def __init__(self, x, y, hp, speed, entity, attack_damage):
        super().__init__(x, y, hp, speed, entity)
        self.attack_damage = attack_damage
        # สำคัญ: เก็บตำแหน่งเป็น Vector เพื่อรักษาค่าทศนิยม (Precision)
        self.pos = pg.math.Vector2(x, y)

    def spawn(self):
        pass

    def update(self, *args, **kwargs):
        player_pos = kwargs.get('player_pos')
        
        if player_pos:
            target_vector = pg.math.Vector2(player_pos)
            current_vector = pg.math.Vector2(self.pos)
            
            direction = target_vector - current_vector
            
            if direction.length() > 0:
                direction = direction.normalize() * self.speed
                # อัปเดตตำแหน่งจริง (ทศนิยม)
                self.pos += direction
                # อัปเดต rect (จำนวนเต็ม) เพื่อใช้ในการวาดภาพและเช็ค Collision
                self.rect.center = (self.pos.x, self.pos.y)

    def attack(self, target=None):
        if target and self.rect.colliderect(target.rect):
            target.take_damage(self.attack_damage)

# --- Zombie Subclasses ---

class NormalZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, 30, 2, "assets/character/zombie/zombie_normal/zombie_normal1.png", 10)

class FastZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 4.5, "assets/character/zombie/zombie_fast/zombie_fast1.png", 5)

class TankZombie(Zombie):
    def __init__(self, x, y):
        super().__init__(x, y, 100, 1, "assets/character/zombie/zombie_tank/zombie_tank1.png", 20)


# --- 3. ส่วนของ Factory (โรงงานสร้างซอมบี้) ---

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