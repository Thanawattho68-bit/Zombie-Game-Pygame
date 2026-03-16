import pygame as pg
import random
import math
from settings import *
import player
import zombie
import weapons

class GameState:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

class MainMenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.menu_index = 0
        self.items = ["START GAME", "SETTINGS", "EXIT"]

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(self.items)
                elif event.key == pg.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(self.items)
                elif event.key == pg.K_RETURN:
                    self.select_option()
            
            if event.type == pg.MOUSEBUTTONDOWN:
                self.handle_mouse_click(event.pos)

        # Mouse hover
        mouse_pos = pg.mouse.get_pos()
        if self.game.start_btn_rect.collidepoint(mouse_pos): self.menu_index = 0
        elif self.game.settings_btn_rect.collidepoint(mouse_pos): self.menu_index = 1
        elif self.game.exit_btn_rect.collidepoint(mouse_pos): self.menu_index = 2

    def select_option(self):
        if self.menu_index == 0:
            self.game.change_state(ModeSelectState(self.game))
        elif self.menu_index == 1:
            self.game.change_state(SettingsState(self.game, self))
        elif self.menu_index == 2:
            self.game.running = False

    def handle_mouse_click(self, pos):
        if self.game.start_btn_rect.collidepoint(pos):
            self.menu_index = 0
            self.select_option()
        elif self.game.settings_btn_rect.collidepoint(pos):
            self.menu_index = 1
            self.select_option()
        elif self.game.exit_btn_rect.collidepoint(pos):
            self.menu_index = 2
            self.select_option()

    def draw(self, screen):
        screen.fill((20, 20, 25))
        
        # Pulse title
        scale = 1.0 + 0.05 * math.sin(pg.time.get_ticks() * 0.005)
        title_font = pg.font.SysFont(None, int(92 * scale))
        
        title_text = "ZOMBIE GAME NAJA"
        glow_surf = title_font.render(title_text, True, (150, 0, 0))
        screen.blit(glow_surf, glow_surf.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//3 + 2)))
        
        title = title_font.render(title_text, True, RED)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3)))

        menu_items_rects = [self.game.start_btn_rect, self.game.settings_btn_rect, self.game.exit_btn_rect]
        for i, item_text in enumerate(self.items):
            is_selected = (self.menu_index == i)
            color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
            rect = menu_items_rects[i]
            
            if is_selected:
                pg.draw.rect(screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), rect, border_radius=10)
                pg.draw.rect(screen, PRIMARY_COLOR, rect, width=3, border_radius=10)
            else:
                pg.draw.rect(screen, (35, 35, 40), rect, border_radius=10)
            
            btn_text = self.game.ui.btn_font.render(item_text, True, color)
            screen.blit(btn_text, btn_text.get_rect(center=rect.center))
        
        hint = self.game.ui.ui_font.render("ARROWS to navigate • ENTER to select", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

class SettingsState(GameState):
    def __init__(self, game, previous_state):
        super().__init__(game)
        self.previous_state = previous_state
        self.settings_index = 0
        self.options = [
            ("MUSIC (BGM)", "vol_bgm"),
            ("SHOOTING", "vol_shoot"),
            ("ZOMBIES", "vol_zombie"),
            ("PLAYER", "vol_player"),
            ("BACK", None)
        ]
        self.dragging = False

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.settings_index = (self.settings_index - 1) % len(self.options)
                elif event.key == pg.K_DOWN:
                    self.settings_index = (self.settings_index + 1) % len(self.options)
                elif event.key == pg.K_ESCAPE or (event.key == pg.K_RETURN and self.settings_index == 4):
                    self.game.change_state(self.previous_state)
                
                # Keyboard volume adjust
                if self.settings_index < 4:
                    attr = self.options[self.settings_index][1]
                    if event.key == pg.K_LEFT:
                        setattr(self.game, attr, max(0.0, getattr(self.game, attr) - 0.05))
                        self.game.update_all_volumes()
                    elif event.key == pg.K_RIGHT:
                        setattr(self.game, attr, min(1.0, getattr(self.game, attr) + 0.05))
                        self.game.update_all_volumes()

            if event.type == pg.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)
            if event.type == pg.MOUSEBUTTONUP:
                self.dragging = False
            if event.type == pg.MOUSEMOTION:
                self.handle_motion(event.pos)

    def handle_click(self, pos):
        for i in range(len(self.options)):
            box_rect = pg.Rect(0, 0, 550, 60)
            box_rect.center = (SCREEN_WIDTH//2, 180 + i * 75)
            if box_rect.collidepoint(pos):
                if i == 4:
                    self.game.change_state(self.previous_state)
                else:
                    self.settings_index = i
                    self.dragging = True
                    self.update_slider(pos)

    def handle_motion(self, pos):
        if self.dragging:
            self.update_slider(pos)
        else:
            for i in range(len(self.options)):
                box_rect = pg.Rect(0, 0, 550, 60)
                box_rect.center = (SCREEN_WIDTH//2, 180 + i * 75)
                if box_rect.collidepoint(pos):
                    self.settings_index = i

    def update_slider(self, pos):
        if self.settings_index >= 4: return
        slider_start_x = SCREEN_WIDTH//2 - 50
        slider_width = 250
        val = (pos[0] - slider_start_x) / slider_width
        val = max(0.0, min(1.0, val))
        attr = self.options[self.settings_index][1]
        setattr(self.game, attr, val)
        self.game.update_all_volumes()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        if isinstance(self.previous_state, (PlayingState, PausedState)):
             # เรียกใช้ draw_background ถ้ามี หรือเรียก draw ปกติถ้าไม่มี (แต่วาดผ่าน overlay)
             if hasattr(self.previous_state, 'draw_background'):
                 self.previous_state.draw_background(screen)
             else:
                 self.previous_state.draw(screen)
                 
             overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
             overlay.fill((0, 0, 0, 150))
             screen.blit(overlay, (0, 0))

        title = self.game.ui.btn_font.render("AUDIO SETTINGS", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        for i, (label, attr) in enumerate(self.options):
            is_selected = (i == self.settings_index)
            box_rect = pg.Rect(0, 0, 550, 60)
            box_rect.center = (SCREEN_WIDTH//2, 180 + i * 75)
            
            if attr:
                val = getattr(self.game, attr)
                self.game.ui.draw_slider(screen, box_rect, label, val, is_selected)
            else:
                self.game.ui.draw_button(screen, box_rect, label, (30, 30, 35), (40, 40, 45), WHITE if not is_selected else PRIMARY_COLOR)

class ModeSelectState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.selected_index = 0
        self.modes = list(self.game.difficulty_map.keys())

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.modes)
                elif event.key == pg.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.modes)
                elif event.key == pg.K_RETURN:
                    self.confirm()
                elif event.key == pg.K_ESCAPE:
                    self.game.change_state(MainMenuState(self.game))
            
            if event.type == pg.MOUSEBUTTONDOWN:
                for i in range(len(self.modes)):
                    box_rect = pg.Rect(0, 0, 450, 80)
                    box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
                    if box_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.confirm()

    def confirm(self):
        mode_name = self.modes[self.selected_index]
        self.game.difficulty_strategy = self.game.difficulty_map[mode_name]()
        self.game.zombie_factory = zombie.ZombieFactory(self.game.difficulty_strategy)
        self.game.change_state(CharSelectState(self.game))

    def draw(self, screen):
        screen.fill(BG_COLOR)
        title = self.game.ui.btn_font.render("GAME MODE", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        for i, mode_name in enumerate(self.modes):
            is_selected = (i == self.selected_index)
            color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
            box_rect = pg.Rect(0, 0, 450, 80)
            box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
            
            if is_selected:
                pg.draw.rect(screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                pg.draw.rect(screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
            else:
                pg.draw.rect(screen, (35, 35, 40), box_rect, border_radius=10)
            
            mode_text = self.game.ui.btn_font.render(mode_name.upper(), True, color)
            screen.blit(mode_text, mode_text.get_rect(center=box_rect.center))
        
        hint = self.game.ui.ui_font.render("ARROWS to switch • ENTER to select • ESC for menu", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

class CharSelectState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.selected_index = 0
        self.chars = self.game.available_chars

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.chars)
                elif event.key == pg.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.chars)
                elif event.key == pg.K_RETURN:
                    self.confirm()
                elif event.key == pg.K_ESCAPE:
                    self.game.change_state(ModeSelectState(self.game))
            
            if event.type == pg.MOUSEBUTTONDOWN:
                for i in range(len(self.chars)):
                    box_rect = pg.Rect(0, 0, 450, 80)
                    box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
                    if box_rect.collidepoint(event.pos):
                        self.selected_index = i
                        self.confirm()

    def confirm(self):
        self.game.selected_char_index = self.selected_index
        self.game.selected_weapon_indices = []
        self.game.change_state(WeaponSelectState(self.game))

    def draw(self, screen):
        screen.fill(BG_COLOR)
        title = self.game.ui.btn_font.render("SELECT YOUR CHARACTER", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        for i, char in enumerate(self.chars):
            is_selected = (i == self.selected_index)
            color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
            box_rect = pg.Rect(0, 0, 450, 80)
            box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
            
            if is_selected:
                pg.draw.rect(screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                pg.draw.rect(screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
            else:
                pg.draw.rect(screen, (35, 35, 40), box_rect, border_radius=10)
            
            preview_img = pg.transform.smoothscale(self.game.char_previews[i], (60, 60))
            img_rect = preview_img.get_rect(midleft=(box_rect.left + 20, box_rect.centery))
            screen.blit(preview_img, img_rect)

            name_text = char.__name__
            char_text = self.game.ui.btn_font.render(name_text, True, color)
            text_rect = char_text.get_rect(midleft=(img_rect.right + 20, box_rect.centery))
            screen.blit(char_text, text_rect)
        
        hint = self.game.ui.ui_font.render("ARROWS to switch • ENTER to select • ESC to go back", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

class WeaponSelectState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.scroll_y = 0
        self.weapons_list = self.game.available_weapons

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEWHEEL:
                self.scroll_y += event.y * 30
                max_scroll = max(0, (len(self.weapons_list) * 100) - 300)
                self.scroll_y = max(-max_scroll, min(0, self.scroll_y))

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    self.scroll_y = min(0, self.scroll_y + 30)
                elif event.key == pg.K_DOWN:
                    max_scroll = max(0, (len(self.weapons_list) * 100) - 300)
                    self.scroll_y = max(-max_scroll, self.scroll_y - 30)
                elif event.key == pg.K_RETURN and len(self.game.selected_weapon_indices) == 2:
                    self.game.reset_game()
                elif event.key == pg.K_ESCAPE:
                    self.game.change_state(CharSelectState(self.game))
            
            if event.type == pg.MOUSEBUTTONDOWN:
                container_w = 650
                start_x = (SCREEN_WIDTH - container_w) // 2
                weapon_x = start_x + 250
                
                for i in range(len(self.weapons_list)):
                    btn_rect = pg.Rect(weapon_x, 200 + i * 100 + self.scroll_y, 400, 80)
                    if btn_rect.collidepoint(event.pos):
                        if i in self.game.selected_weapon_indices:
                            self.game.selected_weapon_indices.remove(i)
                        elif len(self.game.selected_weapon_indices) < 2:
                            self.game.selected_weapon_indices.append(i)
                
                if len(self.game.selected_weapon_indices) == 2:
                    start_rect = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60)
                    if start_rect.collidepoint(event.pos):
                        self.game.reset_game()

    def draw(self, screen):
        screen.fill(BG_COLOR)
        title = self.game.ui.btn_font.render("SELECT 2 WEAPONS", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

        container_w = 650 
        start_x = (SCREEN_WIDTH - container_w) // 2
        char_x = start_x + 100
        weapon_x = start_x + 250

        char_img = pg.transform.smoothscale(self.game.char_previews[self.game.selected_char_index], (140, 140))
        char_rect = char_img.get_rect(center=(char_x, SCREEN_HEIGHT//2 - 40))
        
        bg_rect = pg.Rect(0, 0, 170, 210)
        bg_rect.center = (char_x, SCREEN_HEIGHT//2 - 20)
        pg.draw.rect(screen, (35, 35, 40), bg_rect, border_radius=15)
        pg.draw.rect(screen, PRIMARY_COLOR, bg_rect, width=3, border_radius=15)
        screen.blit(char_img, char_rect)
        
        char_name = self.game.available_chars[self.game.selected_char_index].__name__
        name_surf = self.game.ui.ui_font.render(char_name, True, PRIMARY_COLOR)
        screen.blit(name_surf, name_surf.get_rect(center=(char_x, char_rect.bottom + 30)))

        for i, weapon in enumerate(self.weapons_list):
            is_selected = (i in self.game.selected_weapon_indices)
            color = PRIMARY_COLOR if is_selected else WHITE
            box_rect = pg.Rect(weapon_x, 200 + i * 100 + self.scroll_y, 400, 80)
            
            if box_rect.bottom < 150 or box_rect.top > SCREEN_HEIGHT - 150:
                continue
            
            select_num = f"#{self.game.selected_weapon_indices.index(i) + 1} " if is_selected else ""
            if is_selected:
                pg.draw.rect(screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                pg.draw.rect(screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
            else:
                pg.draw.rect(screen, (35, 35, 40), box_rect, border_radius=10)
            
            weapon_text = self.game.ui.btn_font.render(f"{select_num}{weapon.__name__}", True, color)
            screen.blit(weapon_text, weapon_text.get_rect(center=box_rect.center))
        
        if len(self.game.selected_weapon_indices) == 2:
            start_btn = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60)
            self.game.ui.draw_button(screen, start_btn, "START MISSION", PRIMARY_COLOR, (100, 255, 100), BLACK)
        
        hint = self.game.ui.ui_font.render("Click to select/deselect • Need 2 weapons to start • ESC to go back", True, (180, 180, 180))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.game.change_state(PausedState(self.game))
                    pg.mixer.pause()
                if self.game.player:
                    if event.key == RELOAD:
                        self.game.player.reload_weapon()
                    elif event.key == SWITCH_WEAPON_1:
                        self.switch_weapon(0)
                    elif event.key == SWITCH_WEAPON_2:
                        self.switch_weapon(1)

        if self.game.player:
            keys = pg.key.get_pressed()
            mouse = pg.mouse.get_pressed()
            if keys[SHOOT] or mouse[0]:
                bullet = self.game.player.attack()
                if bullet:
                    self.game.all_sprites.add(bullet)
                    self.game.bullets.add(bullet)

    def switch_weapon(self, index):
        if len(self.game.weapon_instances) > index and self.game.current_weapon_index != index:
            self.game.player.weapon.remove(self.game.all_sprites)
            self.game.current_weapon_index = index
            self.game.player.weapon = self.game.weapon_instances[index]
            self.game.all_sprites.add(self.game.player.weapon)

    def update(self):
        if not self.game.player: return
        
        # Collision
        hits = pg.sprite.groupcollide(self.game.zombies, self.game.bullets, False, True)
        for z, bullet_hits in hits.items():
            for b in bullet_hits:
                if z.take_damage(b.damage):
                    self.game.score += 10
                    
        self.game.all_sprites.update(
            player_pos=self.game.player.rect.center,
            weapon_pos=(self.game.player.rect.centerx, self.game.player.rect.bottom)
        )
        
        now = pg.time.get_ticks()
        for z in pg.sprite.spritecollide(self.game.player, self.game.zombies, False):
            if getattr(self.game, "last_attacked", 0) + self.game.zombie_attack_delay < now:
                z.attack(self.game.player)
                self.game.last_attacked = now
        
        if self.game.player.hp <= 0:
            self.game.change_state(GameOverState(self.game))
            pg.mixer.music.stop()

        if len(self.game.zombies) == 0 and len(self.game.zombie_spawn_queue) == 0:
            self.game.current_wave += 1
            self.game.spawn_wave()

        # Spawn queue
        if self.game.zombie_spawn_queue and now >= self.game.next_spawn_time:
            z = self.game.zombie_spawn_queue.pop()
            self.game.all_sprites.add(z)
            self.game.zombies.add(z)
            self.game.next_spawn_time = now + random.randint(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

    def draw_background(self, screen):
        screen.fill(DARK_GRAY)
        self.game.all_sprites.draw(screen)

    def draw(self, screen):
        self.draw_background(screen)
        
        # Hud
        stat_bar = pg.Surface((SCREEN_WIDTH, 60), pg.SRCALPHA)
        stat_bar.fill((0, 0, 0, 120))
        screen.blit(stat_bar, (0, 0))
        
        if self.game.player:
            stats_text = f'Wave: {self.game.current_wave} | {type(self.game.player.weapon).__name__} | HP: {self.game.player.hp} | Score: {self.game.score} | Ammo: {self.game.player.weapon.current_ammo}/{self.game.player.weapon.magazine_size}'
            stats_img = self.game.ui.ui_font.render(stats_text, True, WHITE)
            screen.blit(stats_img, (20, 15))

class PausedState(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.game.change_state(PlayingState(self.game))
                pg.mixer.unpause()
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.game.continue_btn_rect.collidepoint(event.pos):
                    self.game.change_state(PlayingState(self.game))
                    pg.mixer.unpause()
                elif self.game.return_btn_rect.collidepoint(event.pos):
                    self.game.stop_all_and_menu()
                elif self.game.pause_settings_btn_rect.collidepoint(event.pos):
                    self.game.change_state(SettingsState(self.game, self))

    def draw_background(self, screen):
        # วาด sprites เหมือนเดิมแต่ใช้ชื่อให้ตรงกับที่ PlayingState ใช้
        self.game.all_sprites.draw(screen)

    def draw(self, screen):
        # Draw game in background
        self.draw_background(screen)
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = self.game.font.render("PAUSED", True, WHITE)
        screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 160)))

        self.game.ui.draw_button(screen, self.game.continue_btn_rect, "CONTINUE", (40, 160, 40), (60, 220, 60), BLACK)
        self.game.ui.draw_button(screen, self.game.return_btn_rect, "RETURN TO MENU", (120, 120, 120), (180, 180, 180), BLACK)
        self.game.ui.draw_button(screen, self.game.pause_settings_btn_rect, "SETTINGS", (100, 100, 100), (150, 150, 150), BLACK)

class GameOverState(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.game.stop_all_and_menu()
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.game.restart_button_rect.collidepoint(event.pos):
                    self.game.stop_all_and_menu()

    def draw(self, screen):
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0,0))
        
        msg = self.game.font.render("MISSION FAILED", True, RED)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)))
        
        score_text = self.game.ui.btn_font.render(f"Score: {self.game.score} | Wave: {self.game.current_wave}", True, WHITE)
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        
        self.game.ui.draw_button(screen, self.game.restart_button_rect, "MAIN MENU", (100, 100, 100), (150, 150, 150), BLACK)

class WinState(GameState):
    def handle_events(self, events):
        for event in events:
            if event.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN]:
                self.game.stop_all_and_menu()

    def draw(self, screen):
        overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0,0))
        
        msg = self.game.font.render("MISSION ACCOMPLISHED", True, PRIMARY_COLOR)
        screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)))
        
        score_text = self.game.ui.btn_font.render(f"Score: {self.game.score} | Waves Cleared: {self.game.current_wave - 1}", True, WHITE)
        screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20)))
        
        self.game.ui.draw_button(screen, self.game.restart_button_rect, "MAIN MENU", (40, 160, 40), (60, 220, 60), BLACK)
