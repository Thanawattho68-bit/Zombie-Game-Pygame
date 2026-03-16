import pygame as pg
import random
import os
from settings import *

class SoundComponent:
    def __init__(self, owner, sound_folder, default_volume, categories):
        self.owner = owner
        self.sound_folder = sound_folder
        self.default_volume = default_volume
        self.categories = categories
        self.sounds = {cat: [] for cat in categories}
        self.current_channel = None
        self.current_sound_type = ""
        self._load_sounds()

    def _load_sounds(self):
        if not self.sound_folder or not os.path.exists(self.sound_folder):
            return
            
        for f in os.listdir(self.sound_folder):
            if f.endswith(('.wav', '.ogg', '.mp3')):
                for s_type in self.sounds.keys():
                    if f.startswith(s_type):
                        try:
                            snd = pg.mixer.Sound(os.path.join(self.sound_folder, f))
                            vol = self.default_volume
                            snd.set_volume(vol)
                            self.sounds[s_type].append(snd)
                        except Exception as e:
                            print(f"Warning: Could not load sound '{f}': {e}")

    def set_volume(self, sound_type, volume):
        if sound_type in self.sounds:
            for snd in self.sounds[sound_type]:
                snd.set_volume(max(0.0, min(1.0, volume)))

    @property
    def is_playing(self):
        return self.current_channel is not None and self.current_channel.get_busy()

    def play(self, sound_type):
        priorities = {
            "death": 3,
            "damage": 2,
            "reload": 1,
            "idle": 1
        }
        
        current_priority = priorities.get(self.current_sound_type, -1)
        new_priority = priorities.get(sound_type, 0)

        # 1. ถ้าเสียงใหม่ความสำคัญต่ำกว่าเสียงที่เล่นอยู่ -> ไม่เล่น
        if self.is_playing and new_priority < current_priority:
            return
        
        # 2. กรณีลำดับความสำคัญเท่ากัน (เช่น idle กับ reload)
        if self.is_playing and new_priority == current_priority:
            # ถ้าเป็นกลุ่มเสียงทั่วไป (priority 1 เช่น idle/reload) ห้ามขัดจังหวะกันเอง
            if new_priority <= 1:
                return
            # ถ้าเป็นกลุ่มเสียงสำคัญมาก ให้ขัดจังหวะได้ (หรือตามตรรกะเดิมคือหยุดตัวเก่าเล่นตัวใหม่)
            self.current_channel.stop()

        # 3. ถ้าเสียงใหม่สำคัญกว่าเสียงเดิมที่กำลังเล่นอยู่ -> หยุดตัวเดิมแล้วเล่นตัวใหม่
        if self.is_playing and new_priority > current_priority:
            self.current_channel.stop()

        # 3. เริ่มเล่นเสียงใหม่
        if sound_type in self.sounds and self.sounds[sound_type]:
            ch = random.choice(self.sounds[sound_type]).play()
            if ch:
                self.current_channel = ch
                self.current_sound_type = sound_type
