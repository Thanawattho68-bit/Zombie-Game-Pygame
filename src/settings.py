import pygame as pg

# สถาบันการศึกษากำหนดค่าคอนฟิก (Game Settings)

# Screen Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GRAY = (50, 50, 50)

# UI Colors
BG_COLOR = (20, 20, 25)
PRIMARY_COLOR = (0, 255, 100) # สีเขียวนีออน
SECONDARY_COLOR = (150, 150, 150) # สีเทาสำหรับตอนไม่เลือก

# Player Settings
PLAYER_SPEED = 5
PLAYER_HP = 100

# Sound Settings
SHOOT_VOLUME = 0.2
ZOMBIE_VOLUME = 1
PLAYER_VOLUME = 1
BGM_VOLUME = 0.1

# Keys
WALK_UP = pg.K_w
WALK_DOWN = pg.K_s
WALK_LEFT = pg.K_a
WALK_RIGHT = pg.K_d
SHOOT = pg.K_SPACE
RELOAD = pg.K_r
SWITCH_WEAPON_1 = pg.K_1
SWITCH_WEAPON_2 = pg.K_2

# Spawn Settings (Time in milliseconds)
SPAWN_DELAY_MIN = 500
SPAWN_DELAY_MAX = 2000