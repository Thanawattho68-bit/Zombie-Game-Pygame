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
        pg.mixer.set_num_channels(64)
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
        self.char_previews = []
        for char_cls in self.available_chars:
            try:
                # ใช้ BASE_PATH ที่เราเพิ่มเข้าไปเพื่อหาโฟลเดอร์รูป
                img_path = player.get_random_image(f"{char_cls.BASE_PATH}/image")
                if img_path:
                    img = pg.image.load(img_path).convert_alpha()
                    # เก็บเป็นรูปที่ขนาดใหญ่หน่อยหรือขนาดดั้งเดิมไว้ก่อน เพื่อไม่ให้ pixelated เวลาขยาย
                    # ในที่นี้ขยายเป็น 140x140 (ขนาดสูงสุดที่ใช้) ไว้เลย
                    img = pg.transform.smoothscale(img, (140, 140))
                else:
                    img = pg.Surface((140, 140))
                    img.fill(WHITE)
                self.char_previews.append(img)
            except Exception as e:
                print(f"Error loading preview for {char_cls.__name__}: {e}")
                self.char_previews.append(pg.Surface((140, 140)))

        self.selected_char_index = 0
        self.main_menu_index = 0 # 0: Start, 1: Exit
        
        self.available_weapons = [
            {"name": "Glock 17", "class": Glock},
            {"name": "M16 Rifle", "class": M16}
        ]
        self.selected_weapon_indices = [] # จะเก็บ index ของอาวุธที่เลือก (สูงสุด 2 อัน)
        self.weapon_scroll_y = 0
        
        self.selected_mode_index = 0
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
        self.zombie_spawn_queue = []
        self.next_spawn_time = 0

    def reset_game(self):
        self.game_state = "PLAYING"
        self.current_wave = 1
        self.score = 0
        self.zombie_attack_delay = 500
        
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.zombie_spawn_queue = []
        
        char_class = self.available_chars[self.selected_char_index]
        self.player = char_class(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        self.player.spawn()
        
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
            # เก็บซอมบี้ที่ต้องเกิดใส่ Queue ไว้ ไม่แอดลงจอทันที
            self.zombie_spawn_queue = new_zombies
            # สลับลำดับเพื่อให้ซอมบี้แต่ละชนิดปนกัน
            random.shuffle(self.zombie_spawn_queue)
            # ตั้งเวลาเกิดตัวแรก
            self.next_spawn_time = pg.time.get_ticks() + random.randint(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

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
                            self.game_state = "MODE_SELECT"
                        else:
                            self.running = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.start_btn_rect.collidepoint(event.pos):
                        self.game_state = "MODE_SELECT"
                    elif self.exit_btn_rect.collidepoint(event.pos):
                        self.running = False
                
                # รองรับการเลื่อนเมาส์ไปมาเพื่อเปลี่ยน index
                mouse_pos = pg.mouse.get_pos()
                if self.start_btn_rect.collidepoint(mouse_pos):
                    self.main_menu_index = 0
                elif self.exit_btn_rect.collidepoint(mouse_pos):
                    self.main_menu_index = 1
                    
            elif self.game_state == "MODE_SELECT":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:
                        self.selected_mode_index = (self.selected_mode_index - 1) % len(self.difficulty_map)
                    elif event.key == pg.K_DOWN:
                        self.selected_mode_index = (self.selected_mode_index + 1) % len(self.difficulty_map)
                    elif event.key == pg.K_RETURN:
                        mode_name = list(self.difficulty_map.keys())[self.selected_mode_index]
                        self.difficulty_strategy = self.difficulty_map[mode_name]()
                        self.zombie_factory = zombie.ZombieFactory(self.difficulty_strategy)
                        self.game_state = "CHAR_SELECT"
                    elif event.key == pg.K_ESCAPE:
                        self.game_state = "MAIN_MENU"
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    mode_names = list(self.difficulty_map.keys())
                    for i in range(len(mode_names)):
                        box_rect = pg.Rect(0, 0, 450, 80)
                        box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
                        if box_rect.collidepoint(event.pos):
                            self.selected_mode_index = i
                            mode_name = mode_names[i]
                            self.difficulty_strategy = self.difficulty_map[mode_name]()
                            self.zombie_factory = zombie.ZombieFactory(self.difficulty_strategy)
                            self.game_state = "CHAR_SELECT"

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
                        self.game_state = "MODE_SELECT"
                
                if event.type == pg.MOUSEBUTTONDOWN:
                    for i in range(len(self.available_chars)):
                        box_rect = pg.Rect(0, 0, 450, 80)
                        box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
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
                    # คำนวณตำแหน่งเริ่มต้นของ Container เพื่อให้ตรงกับหน้า draw
                    container_w = 650
                    start_x = (SCREEN_WIDTH - container_w) // 2
                    weapon_x = start_x + 250
                    
                    # ตรวจสอบการคลิกเลือกอาวุธ (ใช้ตำแหน่งใหม่ที่จัดกลาง)
                    for i in range(len(self.available_weapons)):
                        btn_rect = pg.Rect(weapon_x, 200 + i * 100 + self.weapon_scroll_y, 400, 80)
                        if btn_rect.collidepoint(event.pos):
                            if i in self.selected_weapon_indices:
                                self.selected_weapon_indices.remove(i)
                            elif len(self.selected_weapon_indices) < 2:
                                self.selected_weapon_indices.append(i)
                    
                    # ปุ่ม Start หลังเลือกครบ
                    if len(self.selected_weapon_indices) == 2:
                        start_rect = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60)
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
                        pg.mixer.pause() # หยุดเสียงชั่วคราว

            elif self.game_state == "PAUSED":
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        self.game_state = "PLAYING"
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.continue_btn_rect.collidepoint(event.pos):
                        self.game_state = "PLAYING"
                        pg.mixer.unpause() # เล่นสีที่ค้างไว้ต่อ
                    elif self.return_btn_rect.collidepoint(event.pos):
                        pg.mixer.stop() # ล้างเสียงทั้งหมดทิ้ง
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

            if len(self.zombies) == 0 and len(self.zombie_spawn_queue) == 0:
                self.current_wave += 1
                self.spawn_wave()

            # --- ระบบ Spawn ซอมบี้แบบสุ่มจังหวะ ---
            if self.zombie_spawn_queue:
                if now >= self.next_spawn_time:
                    z = self.zombie_spawn_queue.pop()
                    self.all_sprites.add(z)
                    self.zombies.add(z)
                    # สุ่มเวลาเกิดตัวต่อไป
                    self.next_spawn_time = now + random.randint(SPAWN_DELAY_MIN, SPAWN_DELAY_MAX)

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
        self.screen.fill(BG_COLOR)

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
                color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
                rect = item["rect"]
                
                if is_selected:
                    # ใช้สีพื้นหลังที่เข้มขึ้นจาก PRIMARY_COLOR (หาร 4)
                    pg.draw.rect(self.screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), rect, border_radius=10)
                    pg.draw.rect(self.screen, PRIMARY_COLOR, rect, width=3, border_radius=10)
                else:
                    # ใช้สีพื้นหลังที่มืดกว่าพื้นหลังหลักเล็กน้อย
                    pg.draw.rect(self.screen, (35, 35, 40), rect, border_radius=10)
                
                btn_text = self.btn_font.render(item["text"], True, color)
                self.screen.blit(btn_text, btn_text.get_rect(center=rect.center))
            
            hint = self.ui_font.render("ARROWS to navigate • ENTER to select", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

        elif self.game_state == "MODE_SELECT":
            title = self.btn_font.render("GAME MODE", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title, title_rect)

            mode_names = list(self.difficulty_map.keys())
            for i, mode_name in enumerate(mode_names):
                is_selected = (i == self.selected_mode_index)
                color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
                
                box_rect = pg.Rect(0, 0, 450, 80)
                box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
                
                if is_selected:
                    pg.draw.rect(self.screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                    pg.draw.rect(self.screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (35, 35, 40), box_rect, border_radius=10)
                
                mode_text = self.btn_font.render(mode_name.upper(), True, color)
                self.screen.blit(mode_text, mode_text.get_rect(center=box_rect.center))
            
            hint = self.ui_font.render("ARROWS to switch • ENTER to select • ESC for menu", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

        elif self.game_state == "CHAR_SELECT":
            title = self.btn_font.render("SELECT YOUR CHARACTER", True, WHITE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
            self.screen.blit(title, title_rect)

            for i, char in enumerate(self.available_chars):
                is_selected = (i == self.selected_char_index)
                color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
                
                # วาดกรอบเลือก (ขยายขนาดขึ้นเล็กน้อยเพื่อให้ใส่รูปได้)
                box_rect = pg.Rect(0, 0, 450, 80)
                box_rect.center = (SCREEN_WIDTH//2, 200 + i * 95)
                
                if is_selected:
                    pg.draw.rect(self.screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                    pg.draw.rect(self.screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (35, 35, 40), box_rect, border_radius=10)
                
                # 1. วาดรูปตัวละคร Preview (ย่อลงเพื่อแสดงหน้าเลือกตัวละคร)
                preview_img = pg.transform.smoothscale(self.char_previews[i], (60, 60))
                img_rect = preview_img.get_rect(midleft=(box_rect.left + 20, box_rect.centery))
                self.screen.blit(preview_img, img_rect)

                # 2. วาดชื่อตัวละครถัดจากรูป
                name_text = char.__name__
                char_text = self.btn_font.render(name_text, True, color)
                # วาดชื่อขยับไปทางขวารูป
                text_rect = char_text.get_rect(midleft=(img_rect.right + 20, box_rect.centery))
                self.screen.blit(char_text, text_rect)
            
            hint = self.ui_font.render("ARROWS to switch • ENTER to select weapons • ESC for menu", True, (180, 180, 180))
            self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50)))

        elif self.game_state == "WEAPON_SELECT":
            title = self.btn_font.render("SELECT 2 WEAPONS", True, WHITE)
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH//2, 80)))

            # --- คำนวณการจัดกึ่งกลาง Container ---
            container_w = 650 
            start_x = (SCREEN_WIDTH - container_w) // 2
            char_x = start_x + 100
            weapon_x = start_x + 250
            # ----------------------------------

            # --- วาดตัวละครที่เลือกไว้ด้านซ้ายของกลุ่ม ---
            char_img = pg.transform.smoothscale(self.char_previews[self.selected_char_index], (140, 140))
            char_rect = char_img.get_rect(center=(char_x, SCREEN_HEIGHT//2 - 40))
            
            bg_rect = pg.Rect(0, 0, 170, 210)
            bg_rect.center = (char_x, SCREEN_HEIGHT//2 - 20)
            pg.draw.rect(self.screen, (35, 35, 40), bg_rect, border_radius=15)
            pg.draw.rect(self.screen, PRIMARY_COLOR, bg_rect, width=3, border_radius=15)
            self.screen.blit(char_img, char_rect)
            
            char_name = self.available_chars[self.selected_char_index].__name__
            name_surf = self.ui_font.render(char_name, True, PRIMARY_COLOR)
            self.screen.blit(name_surf, name_surf.get_rect(center=(char_x, char_rect.bottom + 30)))

            # --- วาดรายการอาวุธด้านขวาของกลุ่ม ---
            for i, weapon in enumerate(self.available_weapons):
                is_selected = (i in self.selected_weapon_indices)
                color = PRIMARY_COLOR if is_selected else WHITE
                
                # ใช้ weapon_x แทนการใช้ SCREEN_WIDTH//2
                box_rect = pg.Rect(weapon_x, 200 + i * 100 + self.weapon_scroll_y, 400, 80)
                
                if box_rect.bottom < 150 or box_rect.top > SCREEN_HEIGHT - 150:
                    continue
                select_num = ""
                if is_selected:
                    select_num = f"#{self.selected_weapon_indices.index(i) + 1} "
                    pg.draw.rect(self.screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), box_rect, border_radius=10)
                    pg.draw.rect(self.screen, PRIMARY_COLOR, box_rect, width=3, border_radius=10)
                else:
                    pg.draw.rect(self.screen, (35, 35, 40), box_rect, border_radius=10)
                
                weapon_text = self.btn_font.render(f"{select_num}{weapon['name']}", True, color)
                self.screen.blit(weapon_text, weapon_text.get_rect(center=box_rect.center))
            
            if len(self.selected_weapon_indices) == 2:
                start_btn = pg.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT - 120, 300, 60)
                self.draw_button(start_btn, "START MISSION", PRIMARY_COLOR, (100, 255, 100), BLACK)
            
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
                msg_color = RED if (self.player and self.player.hp <= 0) else PRIMARY_COLOR
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
