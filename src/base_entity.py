import pygame as pg
import random
from abc import abstractmethod, ABC
from settings import *
from sound_component import SoundComponent

class BaseEntity(ABC, pg.sprite.Sprite):
    def __init__(self, x, y, hp, speed, image_path, size=(35, 35)):
        super().__init__()
        self.image = self._load_image(image_path, size)
        self.hp = hp
        self.speed = speed
        self.rect = self.image.get_rect(center=(x, y))
        self.sound = None # Will be initialized by subclasses if they need sound

    def _load_image(self, path, size):
        if path:
            try:
                img = pg.image.load(path).convert_alpha()
                return pg.transform.scale(img, size)
            except Exception as e:
                print(f"Warning: Could not load image '{path}' - {e}")
        
        # Fallback placeholder
        surface = pg.Surface(size)
        color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        surface.fill(color)
        pg.draw.rect(surface, WHITE, surface.get_rect(), 2)
        return surface

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    def take_damage(self, damage):
        self.hp -= damage
        if self.sound:
            self.sound.play("damage")
        
        if self.hp <= 0:
            if self.sound:
                self.sound.play("death")
            self.kill()
            return True
        return False

class CombatEntity(BaseEntity):
    """Subclass for entities that can perform attacks (ISP)."""
    @abstractmethod
    def attack(self, target=None):
        """Returns a CombatResult or similar (LSP standardization needed)."""
        pass