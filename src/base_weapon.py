import pygame as pg
import math
import random
import os
from settings import *

class BaseWeapon(pg.sprite.Sprite):
    def __init__(self, x, y, weapon_image_path, bullet_class, magazine_size, reload_time, fire_rate, size=(40, 15)):
        super().__init__()
        try:
            self.original_image = pg.image.load(weapon_image_path).convert_alpha()
            self.original_image = pg.transform.scale(self.original_image, size)
        except Exception as e:
            print(f"Warning: Could not load weapon image '{weapon_image_path}' - {e}")
            self.original_image = pg.Surface(size)
            self.original_image.fill(DARK_GRAY)
        
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.bullet_class = bullet_class
        self.magazine_size = magazine_size
        self.current_ammo = magazine_size
        self.reload_time = reload_time * 1000 # Convert to ms
        self.fire_rate = fire_rate * 1000
        self.last_shot_time = 0
        self.angle = 0
        self.is_reloading = False
        self.reload_start_time = 0
        self._load_sounds(weapon_image_path)

    def _load_sounds(self, weapon_path):
        self.sounds = {"shoot": [], "reload": []}
        try:
            parts = weapon_path.replace('\\', '/').split('/')
            if len(parts) >= 3:
                weapon_name = parts[-3]
                base_snd_path = f"assets/weapon/{weapon_name}/sound"
                
                if not os.path.exists(base_snd_path):
                    return

                for f in os.listdir(base_snd_path):
                    if f.endswith(('.wav', '.ogg', '.mp3')):
                        for s_type in self.sounds.keys():
                            if f.startswith(s_type):
                                try:
                                    snd_obj = pg.mixer.Sound(os.path.join(base_snd_path, f))
                                    snd_obj.set_volume(SHOOT_VOLUME)
                                    self.sounds[s_type].append(snd_obj)
                                except Exception as e:
                                    print(f"Warning: Could not load weapon sound '{f}': {e}")
        except Exception as e:
            print(f"Warning: Failed to setup weapon sound: {e}")

    def set_sound_volume(self, sound_type, volume):
        if hasattr(self, 'sounds') and sound_type in self.sounds:
            for snd in self.sounds[sound_type]:
                snd.set_volume(max(0.0, min(1.0, volume)))

    def play_sound(self, sound_type):
        if hasattr(self, 'sounds') and sound_type in self.sounds and self.sounds[sound_type]:
            prev_channel = getattr(self, '_current_sound_channel', None)
            if prev_channel and prev_channel.get_busy():
                prev_channel.stop()
                    
            snd = random.choice(self.sounds[sound_type])
            channel = snd.play()
            
            self._current_sound_channel = channel
            if channel:
                channel.set_volume(SHOOT_VOLUME)

    def update(self, *args, **kwargs):
        if self.is_reloading:
            now = pg.time.get_ticks()
            if now - self.reload_start_time >= self.reload_time:
                self.current_ammo = self.magazine_size
                self.is_reloading = False

        if 'weapon_pos' in kwargs:
            self.rect.center = kwargs['weapon_pos']
        else:
            player_pos = kwargs.get('player_pos', self.rect.center)
            self.rect.center = player_pos
            
        self.rotate_to_mouse()

    def rotate_to_mouse(self):
        mx, my = pg.mouse.get_pos()
        dx, dy = mx - self.rect.centerx, my - self.rect.centery
        self.angle = math.degrees(math.atan2(dy, -dx))
        
        if dx > 0:
            img_to_rotate = pg.transform.flip(self.original_image, False, True) 
        else:
            img_to_rotate = self.original_image
            
        self.image = pg.transform.rotate(img_to_rotate, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def shoot(self):
        mx, my = pg.mouse.get_pos()
        direction = pg.math.Vector2(mx - self.rect.centerx, my - self.rect.centery)
        
        if direction.length() > 0:
            direction = direction.normalize()
        else:
            direction = pg.math.Vector2(1, 0)
            
        # Use Dependency Injection for Bullet
        return self.bullet_class(self.rect.centerx, self.rect.centery, direction)

    def pull_trigger(self):
        if self.is_reloading:
            return None
            
        now = pg.time.get_ticks()
        if self.current_ammo > 0 and now - self.last_shot_time > self.fire_rate:
            self.current_ammo -= 1
            self.last_shot_time = now
            self.play_sound("shoot")
            return self.shoot()

    def reload(self):
        if self.current_ammo < self.magazine_size and not self.is_reloading:
            self.is_reloading = True
            self.reload_start_time = pg.time.get_ticks()
            self.current_ammo = 0
            self.play_sound("reload")
            return True
        return False
