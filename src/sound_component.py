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
        self.narrate_played = False
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
                            vol = NARRATE_VOLUME if s_type == "narrate" else self.default_volume
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
        if sound_type == "narrate":
            if self.narrate_played:
                return
            self.narrate_played = True

        if sound_type == "death":
            if self.is_playing:
                self.current_channel.stop()
        elif sound_type in ["damage", "shoot"]:
            if sound_type in self.sounds and self.sounds[sound_type]:
                random.choice(self.sounds[sound_type]).play()
            return
        else:
            if self.is_playing:
                if self.current_sound_type == "narrate":
                    return
                if self.current_sound_type in ["idle", "reload"] and sound_type in ["idle", "reload"]:
                    return
                self.current_channel.stop()
        
        if sound_type in self.sounds and self.sounds[sound_type]:
            ch = random.choice(self.sounds[sound_type]).play()
            if ch:
                self.current_channel = ch
                self.current_sound_type = sound_type
