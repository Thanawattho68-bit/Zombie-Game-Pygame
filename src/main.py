import pygame as pg
import sys
import random
import math
from settings import *
import player
import zombie
import wave_difficulty
from base_weapon import Glock, M16

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("ZOMBIE GAME NAJA")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 72)
        self.btn_font = pg.font.SysFont(None, 48)
        self.ui_font = pg.font.SysFont(None, 36)
        self.running = True
        
        # UI Rects (Define once)
        self.start_btn_rect = pg.Rect(0, 0, 280, 60)
        self.start_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        
        self.exit_btn_rect = pg.Rect(0, 0, 280, 60)
        self.exit_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 100)

        self.restart_button_rect = pg.Rect(0, 0, 280, 60)
        self.restart_button_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)

        # Pause Menu Rects
        self.continue_btn_rect = pg.Rect(0, 0, 300, 60)
        self.continue_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40)

        self.return_btn_rect = pg.Rect(0, 0, 300, 60)
        self.return_btn_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60)
        
        # 1. Dependency Injection & Strategy Pattern
        # สร้าง Dictionary ที่เก็บ {ชื่อคลาส: ตัวคลาส} อัตโนมัติ
        self.difficulty_map = {cls.__name__: cls for cls in wave_difficulty.WaveDifficulty.__subclasses__()}
        # เรียกใช้ตามชื่อได้เลย เช่น "Endless" หรือ "Story"
        self.difficulty_strategy = self.difficulty_map["Story"]() 
        
        # 2. Factory Pattern for Zombies container
        self.zombie_factory = zombie.ZombieFactory(self.difficulty_strategy)
        
        self.available_chars = player.Player.__subclasses__()
        self.selected_char_index = 0
        self.main_menu_index = 0 # 0: Start, 1: Exit
        
        self.available_weapons = [
            {"name": "Glock 17", "class": Glock},
            {"name": "M16 Rifle", "class": M16}
        ]
        self.selected_weapon_indices = [] # จะเก็บ index ของอาวุธที่เลือก (สูงสุด 2 อัน)
        self.weapon_scroll_y = 0
        
        self.game_state = "MAIN_MENU"
        
        # Initialize attributes to avoid AttributeError in draw()
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.score = 0
        self.current_wave = 1
        self.player = None
        self.last_attacked = 0
        self.zombie_attack_delay = 500

    def reset_game(self):
        self.game_state = "PLAYING"
        self.current_wave = 1
        self.score = 0
        self.zombie_attack_delay = 500
        
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        
        char_class = self.available_chars[self.selected_char_index]
        self.player = char_class(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        
        # ติดตั้งอาวุธที่เลือกอันแรกเป็นอาวุธเริ่มต้น
        if self.selected_weapon_indices:
            w1_class = self.available_weapons[self.selected_weapon_indices[0]]["class"]
            self.player.weapon.kill() # เอาของเดิมจาก class ออก
            self.player.weapon = w1_class(self.player.rect.centerx, self.player.rect.centery)
        
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.player.weapon)
        self.spawn_wave()

    def spawn_wave(self):
        new_zombies = self.zombie_factory.spawn_wave(self.current_wave)
        if new_zombies is None:
            self.game_state = "GAMEOVER" 
        else:
            for z in new_zombies:
                self.all_sprites.add(z)
                self.zombies.add(z)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            if self.game_state == "MAIN_MENU":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.main_menu_index = (self.main_menu_index - 1) % 2
                    elif event.key == pg.K_DOWN:
                        self.main_menu_index = (self.main_menu_index + 1) % 2
                    elif event.key == pg.K_RETURN:
                        if self.main_menu_index == 0:
                            self.game_state = "CHAR_SELECT"
                        else:
                            self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.start_btn_rect.collidepoint(event.pos):
                        self.game_state = "CHAR_SELECT"
                    elif self.exit_btn_rect.collidepoint(event.pos):
                        self.running = False
                
                # รองรับการเลื่อนเมาส์ไปมาเพื่อเปลี่ยน index
                mouse_pos = pg.mouse.get_pos()
                if self.start_btn_rect.collidepoint(mouse_pos):
                    self.main_menu_index = 0
                elif self.exit_btn_rect.collidepoint(mouse_pos):
                    self.main_menu_index = 1
                    
            elif self.game_state == "GAMEOVER":
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.restart_button_rect.collidepoint(event.pos):
                        self.game_state = "MAIN_MENU"
            
            elif self.game_state == "CHAR_SELECT":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.selected_char_index = (self.selected_char_index - 1) % len(self.available_chars)
                    elif event.key == pg.K_DOWN:
                        self.selected_char_index = (self.selected_char_index + 1) % len(self.available_chars)
                    elif event.key == pg.K_RETURN:
                        self.selected_weapon_indices = [] # ล้างปืนที่เคยเลือก
                        self.weapon_scroll_y = 0 # รีเซ็ต scroll
                        self.game_state = "WEAPON_SELECT"
                    elif event.key == pg.K_ESCAPE:
                        self.game_state = "MAIN_MENU"
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    for i in range(len(self.available_chars)):
                        box_rect = pg.Rect(0, 0, 400, 70)
                        box_rect.center = (SCREEN_WIDTH//2, 200 + i * 90)
                        if box_rect.collidepoint(event.pos):
                            self.selected_char_index = i
                            # ถ้าคลิกซ้ำอันเดิมหรือคลิกเลือกแล้วไปต่อ
                            self.selected_weapon_indices = []
                            self.weapon_scroll_y = 0
                            self.game_state = "WEAPON_SELECT"

            elif self.game_state == "WEAPON_SELECT":
                if event.type == pg.MOUSEWHEEL:
                    self.weapon_scroll_y += event.y * 30
                    # จำกัดขอบเขตการเลื่อน
                    max_scroll = max(0, (len(self.available_weapons) * 100) - 300)
                    self.weapon_scroll_y = max(-max_scroll, min(0, self.weapon_scroll_y))

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.weapon_scroll_y = min(0, self.weapon_scroll_y + 30)
                    elif event.key == pg.K_DOWN:
                        max_scroll = max(0, (len(self.available_weapons) * 100) - 300)
                        self.weapon_scroll_y = max(-max_scroll, self.weapon_scroll_y - 30)
                    elif event.key == pg.K_1:
                        if 0 not in self.selected_weapon_indices:
                            self.selected_weapon_indices.append(0)
                    elif event.key == pg.K_2:
                        if 1 not in self.selected_weapon_indices:
                            self.selected_weapon_indices.append(1)
                    elif event.key == pg.K_BACKSPACE:
                        if self.selected_weapon_indices:
                            self.selected_weapon_indices.pop()
                    elif event.key == pg.K_RETURN:
                        if len(self.selected_weapon_indices) == 2:
                            self.reset_game()
                    elif event.key == pg.K_ESCAPE:
                        self.game_state = "CHAR_SELECT"
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    # ตรวจสอบการคลิกเลือกอาวุธ (ต้องบวกค่า scroll ด้วย)
                    for i in range(len(self.available_weapons)):
                        btn_rect = pg.Rect(SCREEN_WIDTH//2 - 200, 200 + i * 100 + self.weapon_scroll_y, 400, 80)
                        if btn_rect.collidepoint(event.pos):
                            if i in self.selected_weapon_indices:
                                self.selected_weapon_indices.remove(i)
                            elif len(self.selected_weapon_indices) < 2:
                                self.selected_weapon_indices.append(i)
                    
                    # ปุ่ม Start หลังเลือกครบ
                    if len(self.selected_weapon_indices) == 2:
                        start_rect = pg.Rect(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT - 100, 200, 60)
                        if start_rect.collidepoint(event.pos):
                            self.reset_game()

            elif self.game_state == "PLAYING":
                if event.type == pg.KEYDOWN:
                    if self.player:
                        if event.key == RELOAD:
                            self.player.reload_weapon()
                        elif event.key == SWITCH_WEAPON_1:
                            if len(self.selected_weapon_indices) >= 1:
                                self.player.weapon.kill()
                                w_class = self.available_weapons[self.selected_weapon_indices[0]]["class"]
                                self.player.weapon = w_class(self.player.rect.centerx, self.player.rect.centery)
                                self.all_sprites.add(self.player.weapon)
                        elif event.key == SWITCH_WEAPON_2:
                            if len(self.selected_weapon_indices) >= 2:
                                self.player.weapon.kill()
                                w_class = self.available_weapons[self.selected_weapon_indices[1]]["class"]
                                self.player.weapon = w_class(self.player.rect.centerx, self.player.rect.centery)
                                self.all_sprites.add(self.player.weapon)
                    
                    if event.key == pg.K_ESCAPE:
                        self.game_state = "PAUSED"

            elif self.game_state == "PAUSED":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game_state = "PLAYING"
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.continue_btn_rect.collidepoint(event.pos):
                        self.game_state = "PLAYING"
                    elif self.return_btn_rect.collidepoint(event.pos):
                        self.game_state = "MAIN_MENU"

        if self.game_state == "PLAYING":
            if self.player:
                keys = pg.key.get_pressed()
                mouse_pressed = pg.mouse.get_pressed()
                if keys[SHOOT] or mouse_pressed[0]:
                    bullet = self.player.attack()
                    if bullet:
                        self.all_sprites.add(bullet)
                        self.bullets.add(bullet)

    def update(self):
        if self.game_state == "PLAYING":
            if not self.player: return
            
            hits = pg.sprite.groupcollide(self.zombies, self.bullets, False, True)
            for zombie, bullet_hits in hits.items():
                for b in bullet_hits:
                    if zombie.take_damage(b.damage):
                        self.score += 10
                        
            self.all_sprites.update(
                player_pos=self.player.rect.center,
                weapon_pos=(self.player.rect.centerx, self.player.rect.bottom)
            )
            
            now = pg.time.get_ticks()
            if self.player:
                for zombie in pg.sprite.spritecollide(self.player, self.zombies, False):
                    if getattr(self, "last_attacked", 0) + self.zombie_attack_delay < now:
                        zombie.attack(self.player)
                        self.last_attacked = now
                
                if self.player.hp <= 0:
                    self.game_state = "GAMEOVER"

            if len(self.zombies) == 0:
                self.current_wave += 1
                self.spawn_wave()

    def draw_button(self, rect, text, base_color, hover_color, text_color):
        mouse_pos = pg.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color
        
        # วาดเงาปุ่ม
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pg.draw.rect(self.screen, (20, 20, 20), shadow_rect, border_radius=12)
        
        # วาดตัวปุ่ม
        pg.draw.rect(self.screen, color, rect, border_radius=12)
        # วาดขอบปุ่ม
        pg.draw.rect(self.screen, WHITE, rect, width=2, border_radius=12)
        
        # วาดข้อความ
        text_surf = self.btn_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        self.screen.blit(text_surf, text_rect)
        
        return is_hovered


    def draw(self):
        self.screen.fill(BLACK)

        if self.game_state == "MAIN_MENU":
            self.screen.fill((20, 20, 25)) # สีน้ำเงินเข้มจัดๆ แบบหน้าเลือกตัวละคร
            
            # เอฟเฟกต์ชื่อเรื่องเต้นเป็นจังหวะ (Pulse)
            scale = 1.0 + 0.05 * math.sin(pg.time.get_ticks() * 0.005)
            title_font = pg.font.SysFont(None, int(92 * scale))
            
            # วาดแสงเงาสีแดงหลังตัวอักษร (Glow)
            glow_surf = title_font.render("ZOMBIE GAME NAJA", True, (150, 0, 0))
            glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2 + 2, SCREEN_HEIGHT//3 + 2))
            self.screen.blit(glow_surf, glow_rect)
            
            title = title_font.render("ZOMBIE GAME NAJA", True, RED)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//3))
            self.screen.blit(title, title_rect)

            # วาดปุ่มในสไตล์เดียวกับหน้าเลือก character
            menu_items = [
                {"rect": self.start_btn_rect, "text": "START GAME", "idx": 0},
                {"rect": self.exit_btn_rect, "text": "EXIT", "idx": 1}
            ]

            for item in menu_items:
                is_selected = (self.main_menu_index == item["idx"])
                color = GREEN if is_selected else (150, 150, 150)
                rect = item["rect"]
                
                if is_selected:
                    pg.draw.rect(self.screen, (0, 80, 0), rect, border_radius=10)
                    pg.draw.rect(self.screen, GREEN, rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (40, 40, 45), rect, border_radius=10)
                
                btn_text = self.btn_font.render(item["text"], True, color)
                self.screen.blit(btn_text, btn_text.get_rect(center=rect.center))
            
            hint = self.ui_font.render("ARROWS to navigate • ENTER to select", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

        elif self.game_state == "CHAR_SELECT":
            self.screen.fill((20, 20, 25)) # สีน้ำเงินเข้มจัดๆ
            title = self.btn_font.render("SELECT YOUR CHARACTER", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title, title_rect)

            for i, char in enumerate(self.available_chars):
                is_selected = (i == self.selected_char_index)
                color = GREEN if is_selected else (150, 150, 150)
                
                # วาดกรอบเลือก
                box_rect = pg.Rect(0, 0, 400, 70)
                box_rect.center = (SCREEN_WIDTH//2, 200 + i * 90)
                
                if is_selected:
                    pg.draw.rect(self.screen, (0, 80, 0), box_rect, border_radius=10)
                    pg.draw.rect(self.screen, GREEN, box_rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (40, 40, 45), box_rect, border_radius=10)
                
                name_text = char.__name__
                char_text = self.btn_font.render(name_text, True, color)
                self.screen.blit(char_text, char_text.get_rect(center=box_rect.center))
            
            hint = self.ui_font.render("ARROWS to switch • ENTER to select weapons • ESC for menu", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

        elif self.game_state == "WEAPON_SELECT":
            self.screen.fill((25, 20, 20)) # สีน้ำตาลแดงมืดๆ
            title = self.btn_font.render("SELECT 2 WEAPONS", True, WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

            for i, weapon in enumerate(self.available_weapons):
                is_selected = (i in self.selected_weapon_indices)
                color = GREEN if is_selected else WHITE
                
                box_rect = pg.Rect(SCREEN_WIDTH//2 - 200, 200 + i * 100 + self.weapon_scroll_y, 400, 80)
                
                # แสดงแค่ส่วนที่อยู่ในพื้นที่เลือก (Optional clipping but simple translation for now)
                if box_rect.bottom < 150 or box_rect.top > SCREEN_HEIGHT - 150:
                    continue
                select_num = ""
                if is_selected:
                    select_num = f"#{self.selected_weapon_indices.index(i) + 1} "
                    pg.draw.rect(self.screen, (0, 60, 0), box_rect, border_radius=10)
                    pg.draw.rect(self.screen, GREEN, box_rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (45, 40, 40), box_rect, border_radius=10)
                
                weapon_text = self.btn_font.render(f"{select_num}{weapon['name']}", True, color)
                self.screen.blit(weapon_text, weapon_text.get_rect(center=box_rect.center))
            
            if len(self.selected_weapon_indices) == 2:
                start_btn = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60)
                self.draw_button(start_btn, "START MISSION", GREEN, (100, 255, 100), BLACK)
            
            hint = self.ui_font.render("Click to select/deselect • Need 2 weapons to start • ESC to go back", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 40)))

        elif self.game_state == "PLAYING" or self.game_state == "GAMEOVER":
            self.screen.fill(DARK_GRAY)
            self.all_sprites.draw(self.screen)
            
            # กรอบ Status ด้านบน
            stat_bar = pg.Surface((SCREEN_WIDTH, 60), pg.SRCALPHA)
            stat_bar.fill((0, 0, 0, 120))
            self.screen.blit(stat_bar, (0, 0))
            
            if self.player:
                stats_text = f'Wave: {self.current_wave}  |  {self.player.weapon.name}  |  HP: {self.player.hp}  |  Score: {self.score}  |  Ammo: {self.player.weapon.current_ammo}/{self.player.weapon.magazine_size}'
                stats_img = self.ui_font.render(stats_text, True, WHITE)
                self.screen.blit(stats_img, (20, 15))
            
            if self.game_state == "GAMEOVER":
                overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
                overlay.fill((0, 0, 0, 200)) # มืดกว่าปกติ
                self.screen.blit(overlay, (0,0))
                
                msg_text = "MISSION FAILED" if (self.player and self.player.hp <= 0) else "MISSION ACCOMPLISHED"
                msg_color = RED if (self.player and self.player.hp <= 0) else GREEN
                msg = self.font.render(msg_text, True, msg_color)
                self.screen.blit(msg, msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80)))
                
                self.draw_button(self.restart_button_rect, "MAIN MENU", (100, 100, 100), (150, 150, 150), BLACK)

        elif self.game_state == "PAUSED":
            # วาดฉากหลังเกมแบบมัวๆ
            self.screen.fill(DARK_GRAY)
            self.all_sprites.draw(self.screen)

            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            pause_title = self.font.render("PAUSED", True, WHITE)
            self.screen.blit(pause_title, pause_title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 160)))

            self.draw_button(self.continue_btn_rect, "CONTINUE", (40, 160, 40), (60, 220, 60), BLACK)
            self.draw_button(self.return_btn_rect, "RETURN TO MENU", (120, 120, 120), (180, 180, 180), BLACK)

        pg.display.flip()

    def run(self):
        while self.running:
            self.events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pg.quit()

if __name__ == "__main__":
    Game().run()
