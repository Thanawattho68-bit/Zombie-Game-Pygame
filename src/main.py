import pygame as pg
import sys
import random
from settings import *
import player
import zombie
import wave_difficulty
import weapons
from ui_manager import UIManager
from game_states import MainMenuState, PlayingState, WinState

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.set_num_channels(64)
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("ZOMBIE GAME NAJA")
        self.clock = pg.time.Clock()
        
        # Fonts
        self.font = pg.font.SysFont(None, 72)
        self.btn_font = pg.font.SysFont(None, 48)
        self.ui_font = pg.font.SysFont(None, 36)
        
        # Managers
        self.ui = UIManager(self.font, self.btn_font, self.ui_font)
        
        # State
        self.running = True
        self.state = None
        
        # Define Rects used by states (SRP: ideally moved to states, but kept here for shared access)
        self._init_rects()

        # Audio state
        self.vol_bgm = BGM_VOLUME
        self.vol_shoot = SHOOT_VOLUME
        self.vol_zombie = ZOMBIE_VOLUME
        self.vol_player = PLAYER_VOLUME
        self.vol_narrate = NARRATE_VOLUME
        
        # Strategy & Factory
        self.difficulty_map = {cls.__name__: cls for cls in wave_difficulty.WaveDifficulty.__subclasses__()}
        self.difficulty_strategy = self.difficulty_map["Story"]() 
        self.zombie_factory = zombie.ZombieFactory(self.difficulty_strategy)
        
        # Character & Weapon selections
        self.available_chars = player.Player.__subclasses__()
        self.available_weapons = weapons.BaseWeapon.__subclasses__()
        self.char_previews = self._load_previews()
        self.selected_char_index = 0
        self.selected_weapon_indices = []

        # Game Session Data
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.score = 0
        self.current_wave = 1
        self.player = None
        self.last_attacked = 0
        self.zombie_attack_delay = 500
        self.zombie_spawn_queue = []
        self.next_spawn_time = 0
        
        # Start at Main Menu
        self.change_state(MainMenuState(self))

    def _init_rects(self):
        self.start_btn_rect = pg.Rect(0, 0, 280, 60)
        self.start_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)
        self.settings_btn_rect = pg.Rect(0, 0, 280, 60)
        self.settings_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)
        self.exit_btn_rect = pg.Rect(0, 0, 280, 60)
        self.exit_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 140)
        
        self.continue_btn_rect = pg.Rect(0, 0, 300, 60)
        self.continue_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)
        self.return_btn_rect = pg.Rect(0, 0, 300, 60)
        self.return_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)
        self.pause_settings_btn_rect = pg.Rect(0, 0, 300, 60)
        self.pause_settings_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 160)
        
        self.restart_button_rect = pg.Rect(0, 0, 280, 60)
        self.restart_button_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

    def _load_previews(self):
        previews = []
        for char_cls in self.available_chars:
            try:
                img_path = player.get_random_image(f"{char_cls.BASE_PATH}/image")
                img = pg.image.load(img_path).convert_alpha() if img_path else pg.Surface((140, 140))
                previews.append(pg.transform.smoothscale(img, (140, 140)))
            except:
                previews.append(pg.Surface((140, 140)))
        return previews

    def change_state(self, new_state):
        self.state = new_state

    def reset_game(self):
        self.current_wave = 1
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        
        char_class = self.available_chars[self.selected_char_index]
        self.player = char_class(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.player.spawn()
        
        self.weapon_instances = [self.available_weapons[idx](0, 0) for idx in self.selected_weapon_indices]
        self.current_weapon_index = 0
        if self.weapon_instances:
            self.player.weapon = self.weapon_instances[0]
        
        self.all_sprites.add(self.player, self.player.weapon)
        self.spawn_wave()
        self._setup_bgm()
        self.change_state(PlayingState(self))

    def _setup_bgm(self):
        bgm_path = "assets/sound/bgm/bgm_1.mp3"
        try:
            if pg.mixer.music.get_busy(): pg.mixer.music.stop()
            pg.mixer.music.load(bgm_path)
            pg.mixer.music.set_volume(self.vol_bgm)
            pg.mixer.music.play(-1)
        except: pass

    def spawn_wave(self):
        new_zombies = self.zombie_factory.spawn_wave(self.current_wave)
        if new_zombies is None:
            self.change_state(WinState(self))
            pg.mixer.music.stop()
        else:
            self.zombie_spawn_queue = new_zombies
            random.shuffle(self.zombie_spawn_queue)
            self.next_spawn_time = pg.time.get_ticks() + random.randint(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

    def update_all_volumes(self):
        pg.mixer.music.set_volume(self.vol_bgm)
        for sprite in self.all_sprites:
            if hasattr(sprite, 'sound') and sprite.sound:
                if isinstance(sprite, player.Player):
                    for cat in ["damage", "death", "reload", "idle"]: sprite.sound.set_volume(cat, self.vol_player)
                    sprite.sound.set_volume("narrate", self.vol_narrate)
                elif isinstance(sprite, zombie.Zombie):
                    for cat in ["idle", "damage", "death"]: sprite.sound.set_volume(cat, self.vol_zombie)
            
            if hasattr(sprite, 'weapon') and sprite.weapon:
                sprite.weapon.set_sound_volume("shoot", self.vol_shoot)
                sprite.weapon.set_sound_volume("reload", self.vol_shoot)

    def stop_all_and_menu(self):
        pg.mixer.stop()
        pg.mixer.music.stop()
        self.change_state(MainMenuState(self))

    def run(self):
        while self.running:
            events = pg.event.get()
            for event in events:
                if event.type == pg.QUIT: self.running = False
            
            self.state.handle_events(events)
            self.state.update()
            self.state.draw(self.screen)
            
            pg.display.flip()
            self.clock.tick(FPS)
        pg.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
