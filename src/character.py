import pygame as pg
import random
import os
from base_entity import BaseEntity
from settings import *
from wave_difficulty import WaveDifficulty
from base_weapon import Glock, M16

# --- Helper Functions ---

def get_random_image(folder_path):
    """
    ฟังก์ชันช่วยสุ่มไฟล์รูปในโฟลเดอร์ที่กำหนด
    ถ้ารูปในโฟลเดอร์มีมากกว่า 1 รูป มันจะสุ่มหยิบมา 1 รูป
    ถ้าโฟลเดอร์ไม่มีอยู่จริง หรือไม่มีรูป จะส่งค่า None กลับไป
    """
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
        if images:
            return os.path.join(folder_path, random.choice(images))
    return None

# --- 2. ส่วนของ Entities (ตัวละคร) ---

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


class Zombie(BaseEntity):
    def __init__(self, x, y, hp, speed, entity, attack_damage, sound_folder, size=(35, 35)):
        super().__init__(x, y, hp, speed, entity, size=size)
        self.attack_damage = attack_damage
        self.pos = pg.math.Vector2(x, y)
        self.sound_folder = sound_folder
        self._load_sounds()
        self.next_idle_sound_time = pg.time.get_ticks() + random.randint(2000, 8000)

    def _load_sounds(self):
        self.sounds = {"idle": [], "death": [], "damage": []}
        if not os.path.exists(self.sound_folder):
            print(f"Warning: Zombie sound folder not found '{self.sound_folder}'")
            return
            
        for f in os.listdir(self.sound_folder):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                for s_type in self.sounds.keys():
                    if f.startswith(s_type):
                        try:
                            snd = pg.mixer.Sound(os.path.join(self.sound_folder, f))
                            self.sounds[s_type].append(snd)
                        except Exception as e:
                            print(f"Warning: Could not load zombie sound '{f}': {e}")

    def spawn(self):
        pass

    def play_sound(self, sound_type):
        if hasattr(self, 'sounds') and sound_type in self.sounds and self.sounds[sound_type]:
            random.choice(self.sounds[sound_type]).play()

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

        # สุ่มเล่นเสียง Idle
        now = pg.time.get_ticks()
        if now >= self.next_idle_sound_time:
            self.play_sound("idle")
            self.next_idle_sound_time = now + random.randint(3000, 10000)

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
