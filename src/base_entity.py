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
        self.next_narrate_time = 0 # เพิ่มตัวแปรคุมจังหวะ narrate
        self.current_channel = None
        self.current_sound_type = ""
        self.narrate_played = False
    
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
                            # ใช้ระดับเสียงตามประเภท
                            vol = NARRATE_VOLUME if s_type == "narrate" else volume
                            snd.set_volume(vol)
                            self.sounds[s_type].append(snd)
                        except Exception as e:
                            print(f"Warning: Could not load sound '{f}' for {self.__class__.__name__}: {e}")

    def set_sound_volume(self, sound_type, volume):
        #จำกัดความดังของเสียงที่ต้องการ (ค่า volume ระหว่าง 0.0 - 1.0)
        if sound_type in self.sounds:
            for snd in self.sounds[sound_type]:
                snd.set_volume(max(0.0, min(1.0, volume)))

    @property
    def sound_is_play(self):
        #เช็คว่าตัวละครนี้กำลังเล่นเสียงอยู่หรือไม่
        return self.current_channel is not None and self.current_channel.get_busy()

    def play_sound(self, sound_type):
        # 1. จัดการเรื่อง narrate (เล่นได้แค่ครั้งเดียวต่อ match)
        if sound_type == "narrate":
            if self.narrate_played:
                return
            self.narrate_played = True

        # 2. กฎลำดับความสำคัญ (Precedence Logic)
        if sound_type == "death":
            # กฎ: Death หยุดทุกเสียงที่กำลังเล่นอยู่
            if self.sound_is_play:
                self.current_channel.stop()
        elif sound_type in ["damage", "shoot"]:
            # กฎ: Damage และ Shoot เล่นทับกับเสียงอื่นได้เลย (Overlap)
            if sound_type in self.sounds and self.sounds[sound_type]:
                random.choice(self.sounds[sound_type]).play()
            return # จบการทำงานตรงนี้เลย ไม่ส่งผลต่อ current_channel
        else:
            # เสียง Action ทั่วไป (idle, reload, ฯลฯ)
            if self.sound_is_play:
                # 1. กฎ: ถ้ากำลังเล่น Narrate อยู่ ห้ามเสียง Action ทั่วไปมาขัด
                if self.current_sound_type == "narrate":
                    return
                
                # 2. กฎใหม่: Mutually Exclusive (idle และ reload ห้ามเล่นแทรกกัน ใครมาก่อนได้เล่นก่อน)
                # ถ้ากำลังเล่น idle อยู่ จะเริ่ม reload ไม่ได้ หรือกำลัง reload อยู่ จะเริ่ม idle ไม่ได้
                if self.current_sound_type in ["idle", "reload"] and sound_type in ["idle", "reload"]:
                    return
                
                # 3. กฎ Action อื่นๆ: ถ้าไม่ใช่กลุ่ม idle/reload (และไม่ใช่ Narrate) ให้หยุดของเดิมก่อนเริ่มอันใหม่
                self.current_channel.stop()
        
        # 3. เริ่มเล่นเสียงใหม่และบันทึกสถานะ (ยกเว้นกลุ่ม Overlap ที่แยกไปแล้ว)
        if sound_type in self.sounds and self.sounds[sound_type]:
            ch = random.choice(self.sounds[sound_type]).play()
            if ch:
                self.current_channel = ch
                self.current_sound_type = sound_type

    def handle_idle_sound(self, min_delay_ms, max_delay_ms):
        #จัดการการเล่นเสียง Idle ตามช่วงเวลาที่กำหนด
        now = pg.time.get_ticks()
        if self.next_idle_sound_time == 0: # เริ่มต้นครั้งแรก
             self.next_idle_sound_time = now + random.randint(min_delay_ms, max_delay_ms)
             
        if now >= self.next_idle_sound_time:
            self.play_sound("idle")
            self.next_idle_sound_time = now + random.randint(min_delay_ms, max_delay_ms)

    def handle_narrate_sound(self, min_delay_ms, max_delay_ms):
        """สุ่มหาจังหวะพูดบรรยาย (Narrate) เพียงครั้งเดียวใน match"""
        if self.narrate_played: # ถ้าเคยเล่นไปแล้วไม่ต้องทำอะไร
            return
            
        now = pg.time.get_ticks()
        if self.next_narrate_time == 0: # ตั้งเวลาสุ่มครั้งแรก
            self.next_narrate_time = now + random.randint(min_delay_ms, max_delay_ms)
            
        if now >= self.next_narrate_time:
            self.play_sound("narrate")

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