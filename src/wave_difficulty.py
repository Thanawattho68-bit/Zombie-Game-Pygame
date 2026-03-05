import pygame as pg
from abc import ABC, abstractmethod
from settings import *

class WaveDifficulty(ABC):
    @abstractmethod
    def get_zombie_stats(self, wave_num):
        pass

class Endless(WaveDifficulty):
    def get_zombie_stats(self, wave_num):
        for i in range(wave_num):
            wave.append((ZOMBIE_NORMAL_HP * wave_num, ZOMBIE_NORMAL_SPEED * wave_num))
            wave.append((ZOMBIE_FAST_HP * wave_num, ZOMBIE_FAST_SPEED * wave_num))
            wave.append((ZOMBIE_TANK_HP * wave_num, ZOMBIE_TANK_SPEED * wave_num))
        return wave

class Story(WaveDifficulty):
    def get_zombie_stats(self, wave_num):
        if wave_num == 3:
            return (ZOMBIE_FAST_HP * wave_num, ZOMBIE_FAST_SPEED * wave_num)
        elif wave_num == 5:
            return (ZOMBIE_TANK_HP * wave_num, ZOMBIE_TANK_SPEED * wave_num)
        else:
            return (ZOMBIE_NORMAL_HP * wave_num, ZOMBIE_NORMAL_SPEED * wave_num)