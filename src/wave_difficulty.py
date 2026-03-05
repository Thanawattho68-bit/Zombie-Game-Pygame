import pygame as pg
from abc import ABC, abstractmethod

# 1. แม่แบบของกติกาเกม (Strategy Interface)
class WaveDifficulty(ABC):
    @abstractmethod
    def get_spawn_config(self, wave_num):
        """คืนค่า 'จำนวน' ของซอมบี้แต่ละชนิดที่จะให้เกิดใน Wave นี้ (นี่คือ Container ที่น้องต้องการ)"""
        pass

# 2. กลยุทธ์แบบ Endless (ความยากเพิ่มขึ้นเรื่อยๆ ไม่มีที่สิ้นสุด)
class Endless(WaveDifficulty):
    def get_spawn_config(self, wave_num):
        # คืนค่าเป็น Dictionary ว่าตัวไหนควรเกิดกี่ตัว
        return {
            "normal": 5 + (wave_num * 2),  # ปกติจะเพิ่มด่านละ 2 ตัว
            "fast": 0 + (wave_num // 2),   # ตัวเร็วจะเริ่มโผล่ตอนด่าน 2
            "tank": 0 + (wave_num // 5)    # ตัวอึดจะเริ่มโผล่ตอนด่าน 5
        }

# 3. กลยุทธ์แบบ Story (ออกแบบความยากไว้ล่วงหน้า มีจุดจบ)
class Story(WaveDifficulty):
    def get_spawn_config(self, wave_num):
        # กำหนดจำนวนศัตรูแบบเป๊ะๆ ในทุกด่าน
        config = {
            1: {"normal": 5, "fast": 0, "tank": 0},
            2: {"normal": 8, "fast": 2, "tank": 0},
            3: {"normal": 10, "fast": 5, "tank": 1} # ด่านบอส
        }
        return config.get(wave_num, None) # ถ้าเกินด่าน 3 ให้ส่ง None เพื่อจบเกม
