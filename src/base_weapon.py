import pygame as pg
import math
from settings import *
from base_bullet import NineMM, FiveFiveSix

class BaseWeapon(pg.sprite.Sprite):
    def __init__(self, x, y, weapon, bullet_type, magazine_size, reload_time, fire_rate, size=(40, 15)):
        super().__init__()
        try:
            self.original_image = pg.image.load(weapon).convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, size)
        except Exception as e:
            print(f"Warning: Could not load weapon image '{weapon}' - {e}")
            self.original_image = pg.Surface(size)
            self.original_image.fill(DARK_GRAY)
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_type = bullet_type
        self.magazine_size = magazine_size
        self.current_ammo = magazine_size
        self.reload_time = reload_time * 1000 # แปลงเป็นมิลลิวินาที
        self.fire_rate = fire_rate * 1000
        self.last_shot_time = 0
        self.angle = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self._load_sounds(weapon)

    def _load_sounds(self, weapon_path):
        self.sounds = {}
        # ดึงว่าปืนนี้คือปืนอะไรจากชื่อโพลเดอร์ อิงจาก path เช่น assets/weapon/glock/image/glock.png -> glock (ind -3)
        try:
            weapon_name = weapon_path.split('/')[-3]
            base_snd_path = f"assets/weapon/{weapon_name}/sound"
            
            # โหลดทีละไฟล์เผื่อบางไฟล์ไม่มี
            for snd in ["shoot", "reload"]:
                snd_file = f"{base_snd_path}/{snd}_1.wav"
                try:
                    snd_obj = pg.mixer.Sound(snd_file)
                    # ลดความดังเสียงปืนเริ่มต้นไม่ให้หูแตก อ้างอิงจาก settings.py
                    if snd == "shoot":
                        snd_obj.set_volume(SHOOT_VOLUME)
                    self.sounds[snd] = snd_obj
                except Exception as e:
                    print(f"Warning: Could not load weapon sound '{snd_file}': {e}")
        except Exception as e:
            print(f"Warning: Failed to setup weapon sounding error: {e}")

    def set_sound_volume(self, sound_type, volume):
        """จำกัดความดังของเสียงที่ต้องการ (ค่า volume ระหว่าง 0.0 - 1.0)"""
        if hasattr(self, 'sounds') and sound_type in self.sounds:
            self.sounds[sound_type].set_volume(max(0.0, min(1.0, volume)))

    def play_sound(self, sound_type):
        if hasattr(self, 'sounds') and sound_type in self.sounds:
            self.sounds[sound_type].play()

    def update(self, *args, **kwargs):
        # เช็คว่ากำลัง Reload อยู่หรือเปล่า
        if self.is_reloading:
            now = pg.time.get_ticks()
            if now - self.reload_start_time >= self.reload_time:
                self.current_ammo = self.magazine_size
                self.is_reloading = False

        player_pos = kwargs.get('player_pos', self.rect.center)
        if hasattr(self, 'owner_center'):
            # In case it's directly assigned instead
            pass
        self.rect.center = player_pos
        self.rotate_to_mouse()

    def rotate_to_mouse(self):
        mx, my = pg.mouse.get_pos()
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, -dx))
        
        # ถ้าเมาส์อยู่ด้านซ้ายของปืน (dx < 0) ให้พลิกรูปแนวแกน Y ก่อนหมุน เพื่อไม่ให้ปืนกลับหัว
        if dx > 0:
            img_to_rotate = pg.transform.flip(self.original_image, False, True) 
        else:
            img_to_rotate = self.original_image
            
        self.image = pg.transform.rotate(img_to_rotate, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        # ให้กระสุนพุ่งไปหาตำแหน่งของเมาส์โดยตรงเลย (ไม่ต้องสนว่าปืนหมุนไปกี่องศา)
        mx, my = pg.mouse.get_pos()
        direction = pg.math.Vector2(mx - self.rect.centerx, my - self.rect.centery)
        
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = pg.math.Vector2(1, 0)
            
        return self.bullet_type(self.rect.centerx, self.rect.centery, direction)

    def pull_trigger(self):
        # ถ้ารีโหลดอยู่ ห้ามยิง
        if self.is_reloading:
            return None
            
        now = pg.time.get_ticks() # ต้องดึงเวลาปัจจุบันมาด้วย
        if self.current_ammo > 0 and now - self.last_shot_time > self.fire_rate:
            # ต้องเช็คด้วยว่า เวลาผ่านไปนานพอหรือยัง (now - last_shot > delay)
            self.current_ammo -= 1
            self.last_shot_time = now
            self.play_sound("shoot")
            return self.shoot()

    def reload(self):
        if self.current_ammo < self.magazine_size and not self.is_reloading:
            self.is_reloading = True
            self.reload_start_time = pg.time.get_ticks()
            self.current_ammo = 0 # เซ็ตให้เหลือ 0 ระหว่างการโหลด
            self.play_sound("reload")
            return True
        return False
    
class Glock(BaseWeapon):
    def __init__(self, x, y):
        # เราขอแค่ x, y เพื่อรู้ว่าจะให้ปืนเกิดตรงไหน
        # ส่วนค่าอื่นๆ เรา (Glock) รู้ดีอยู่แล้วว่าเราคืออะไร
        super().__init__(
            x, y, 
            "assets/weapon/glock/image/glock.png",  # weapon
            NineMM,                           # bullet_type
            15,                               # magazine_size (L4D2 Pistol)
            1,                                # reload_time
            0.175,                            # fire_rate
            size=(30, 15)                     # ขนาดปืนพก
        )

class M16(BaseWeapon):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            "assets/weapon/m16/image/m16.png", 
            FiveFiveSix, 
            50,                               # magazine_size (L4D2 M16)
            2,                                # reload_time
            0.087,                            # fire_rate
            size=(60, 20) # ขนาดปืนไรเฟิลจะยาวกว่าปกติ
        )
