import pygame as pg
import random
import os
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
        
        # ระบบเสียงส่วนกลาง
        self.sounds = {}
        self.sound_folder = ""
        self.next_idle_sound_time = 0
    
    @abstractmethod
    def spawn(self):
        pass

    @abstractmethod
    def update(self):
        pass

    def _load_sounds(self, sound_folder, volume, categories):
        self.sound_folder = sound_folder
        self.sounds = {cat: [] for cat in categories}
        
        if not sound_folder or not os.path.exists(sound_folder):
            return
            
        for f in os.listdir(sound_folder):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                for s_type in self.sounds.keys():
                    if f.startswith(s_type):
                        try:
                            snd = pg.mixer.Sound(os.path.join(sound_folder, f))
                            snd.set_volume(volume)
                            self.sounds[s_type].append(snd)
                        except Exception as e:
                            print(f"Warning: Could not load sound '{f}' for {self.__class__.__name__}: {e}")

    def set_sound_volume(self, sound_type, volume):
        #จำกัดความดังของเสียงที่ต้องการ (ค่า volume ระหว่าง 0.0 - 1.0)
        if sound_type in self.sounds:
            for snd in self.sounds[sound_type]:
                snd.set_volume(max(0.0, min(1.0, volume)))

    def play_sound(self, sound_type):
        if sound_type in self.sounds and self.sounds[sound_type]:
            random.choice(self.sounds[sound_type]).play()

    def handle_idle_sound(self, min_delay_ms, max_delay_ms):
        #จัดการการเล่นเสียง Idle ตามช่วงเวลาที่กำหนด
        now = pg.time.get_ticks()
        if self.next_idle_sound_time == 0: # เริ่มต้นครั้งแรก
             self.next_idle_sound_time = now + random.randint(min_delay_ms, max_delay_ms)
             
        if now >= self.next_idle_sound_time:
            self.play_sound("idle")
            self.next_idle_sound_time = now + random.randint(min_delay_ms, max_delay_ms)

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