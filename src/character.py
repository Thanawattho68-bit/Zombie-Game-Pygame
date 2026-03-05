import pygame as pg
from base_entity import BaseEntity
from settings import *

class Player(BaseEntity):
    def __init__(self, x, y, hp, speed, entity):
        super().__init__(x, y, hp, speed, entity)

    def spawn(self):
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def update(self, *args, **kwargs):
        keys = pg.key.get_pressed()
        if keys[pg.K_a]: self.rect.x -= self.speed
        if keys[pg.K_d]: self.rect.x += self.speed
        if keys[pg.K_w]: self.rect.y -= self.speed
        if keys[pg.K_s]: self.rect.y += self.speed

        # ป้องกันไม่ให้ตัวละครออกนอกหน้าจอ
        self.rect.clamp_ip(pg.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def attack(self, target):
        pass

class Zombie(BaseEntity):
    def __init__(self, x, y, hp, speed, entity):
        super().__init__(x, y, hp, speed, entity)

    def spawn(self):
        pass

    def update(self, *args, **kwargs):
        # 1. รับค่าตำแหน่งผู้เล่น (เราส่งมาทาง args[0] หรือ kwargs)
        # สมมติเราส่งพิกัด center ของผู้เล่นมา
        player_pos = tuple(kwargs.get('player_pos'))
        
        if player_pos:
            # 2. สร้างพิกัดเวกเตอร์
            target_vector = pg.math.Vector2(player_pos)
            zombie_vector = pg.math.Vector2(self.rect.center)
            
            # 3. หาทิศทาง (เป้าหมาย - ตัวเรา)
            direction = target_vector - zombie_vector
            
            # 4. เช็คระยะทาง (ถ้าไม่เป็น 0 ให้ขยับ)
            if direction.length() > 0:
                # ทำให้ความยาวเวกเตอร์เหลือ 1 (ทิศทาง) แล้วคูณด้วยความเร็ว
                direction = direction.normalize() * self.speed
                
                # 5. อัปเดตพิกัด (ต้องเก็บเป็นทศนิยมเพื่อความแม่นยำ)
                # เพื่อความง่ายสำหรับมือใหม่ เราจะอัปเดต rect โดยตรง
                self.rect.x += direction.x
                self.rect.y += direction.y

    def attack(self, target):
        pass