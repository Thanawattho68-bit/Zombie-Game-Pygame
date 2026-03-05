import pygame as pg
import sys
import random
from settings import *
from character import Player, ZombieFactory
from wave_difficulty import Endless
from base_weapon import Glock, M16

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Zombie Survival")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 48)
        self.running = True
        
        # 1. Dependency Injection & Strategy Pattern
        self.difficulty_strategy = Endless()
        
        # 2. Factory Pattern for Zombies container
        self.zombie_factory = ZombieFactory(self.difficulty_strategy)
        
        self.reset_game()

    def reset_game(self):
        self.game_state = "PLAYING" # PLAYING or GAMEOVER
        self.current_wave = 1
        self.score = 0
        self.zombie_attack_delay = 500  # ป้องกันโดนโจมตีรัวๆ ในพริบตา
        
        # กลุ่ม Sprite
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        
        # ตัวละครหลัก
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PLAYER_HP, PLAYER_SPEED, "assets/character/player/player.png")
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.player.weapon)
        
        # Spawn ด่านแรก
        self.spawn_wave()

    def spawn_wave(self):
        new_zombies = self.zombie_factory.spawn_wave(self.current_wave)
        if new_zombies is None:
            # จบโหมด Story
            self.game_state = "GAMEOVER" 
        else:
            for z in new_zombies:
                self.all_sprites.add(z)
                self.zombies.add(z)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            if self.game_state == "GAMEOVER":
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if self.restart_button_rect.collidepoint(mouse_pos):
                        self.reset_game()
            
            elif self.game_state == "PLAYING":
                # กดรัวไม่ได้ ป้องกันการเกิดบั๊กเปลี่ยนปืนรัวๆ (Single Press)
                if event.type == pg.KEYDOWN:
                    if event.key == RELOAD:
                        self.player.weapon.reload()
                    elif event.key == SWITCH_WEAPON_1:
                        self.player.weapon.kill()
                        self.player.weapon = Glock(self.player.rect.centerx, self.player.rect.centery)
                        self.all_sprites.add(self.player.weapon)
                    elif event.key == SWITCH_WEAPON_2:
                        self.player.weapon.kill()
                        self.player.weapon = M16(self.player.rect.centerx, self.player.rect.centery)
                        self.all_sprites.add(self.player.weapon)

        if self.game_state == "PLAYING":
            keys = pg.key.get_pressed()
            # การยิงแบบรัว (Holding Button) ให้ขึ้นอยู่กับ Fire Rate ของปืนนั้นๆ
            if keys[SHOOT]:
                bullet = self.player.attack()
                if bullet:
                    self.all_sprites.add(bullet)
                    self.bullets.add(bullet)

    def update(self):
        if self.game_state == "PLAYING":
            # ส่งพิกัดเป้าหมายไปให้ซอมบี้
            self.all_sprites.update(player_pos=self.player.rect.center)
            
            # เช็คการชนกันระหว่างกระสุนและซอมบี้ (การคืนค่า True ฝั่งกระสุนหมายถึงลบกระสุนทิ้ง)
            hits = pg.sprite.groupcollide(self.zombies, self.bullets, False, True)
            for zombie, bullet_hits in hits.items():
                for b in bullet_hits:
                    # ถ้าซอมบี้ตาย ให้เพิ่มคะแนน
                    if zombie.take_damage(b.damage):
                        self.score += 10
            
            # เช็คว่าผู้เล่นโดนซอมบี้โจมตีไหม
            # ใช้ pygame.time เพื่อหน่วงเวลาโจมตี
            now = pg.time.get_ticks()
            for zombie in pg.sprite.spritecollide(self.player, self.zombies, False):
                # โจมตีและเช็คว่าโดนดาเมจ
                if getattr(self, "last_attacked", 0) + self.zombie_attack_delay < now:
                    zombie.attack(self.player)
                    self.last_attacked = now
            
            if self.player.hp <= 0:
                self.game_state = "GAMEOVER"

            # ข้ามไปด่านถัดไปเมื่อซอมบี้หมด
            if len(self.zombies) == 0:
                self.current_wave += 1
                self.spawn_wave()

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.all_sprites.draw(self.screen)
        
        # UI (ใช้ Dependency ของ Settings โดยตรง)
        ui_font = pg.font.SysFont(None, 36)
        stats_text = f'Wave: {self.current_wave}  |  HP: {self.player.hp}  |  Score: {self.score}  |  Ammo: {self.player.weapon.current_ammo}/{self.player.weapon.magazine_size}'
        stats_img = ui_font.render(stats_text, True, WHITE)
        self.screen.blit(stats_img, (20, 20))
        
        if self.game_state == "GAMEOVER":
            # วาด Overlay
            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0,0))
            
            msg_text = "GAME OVER" if self.player.hp <= 0 else "YOU WIN!"
            msg = self.font.render(msg_text, True, RED if self.player.hp <= 0 else GREEN)
            msg_rect = msg.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(msg, msg_rect)
            
            # Restart Button
            self.restart_button_rect = pg.Rect(0, 0, 200, 60)
            self.restart_button_rect.center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50)
            pg.draw.rect(self.screen, WHITE, self.restart_button_rect, border_radius=10)
            
            btn_text = self.font.render("RESTART", True, BLACK)
            btn_text_rect = btn_text.get_rect(center=self.restart_button_rect.center)
            self.screen.blit(btn_text, btn_text_rect)

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
