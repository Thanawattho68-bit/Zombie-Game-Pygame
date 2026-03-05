import pygame as pg
import sys
import random
from settings import *
from character import Player, NormalZombie, FastZombie, TankZombie
from wave_difficulty import Endless

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("Zombie Survival")
        self.clock = pg.time.Clock()
        self.font = pg.font.SysFont(None, 48)
        self.running = True
        self.reset_game()

    def reset_game(self):
        # 1. สถานะเกม
        self.game_state = "PLAYING" # PLAYING or GAMEOVER
        self.difficulty_manager = Endless()
        self.current_wave = 1
        self.spawn_timer = 0
        self.score = 0
        
        # 2. กลุ่ม Sprite
        self.all_sprites = pg.sprite.Group()
        self.zombies = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        
        # 3. ตัวละครหลัก
        self.player = Player(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, PLAYER_HP, PLAYER_SPEED, "assets/character/player/player.png")
        self.all_sprites.add(self.player)
        self.all_sprites.add(self.player.weapon)

    def spawn_zombie(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top': x, y = random.randint(0, SCREEN_WIDTH), -50
        elif side == 'bottom': x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 50
        elif side == 'left': x, y = -50, random.randint(0, SCREEN_HEIGHT)
        else: x, y = SCREEN_WIDTH + 50, random.randint(0, SCREEN_HEIGHT)

        z_type = random.choices(['normal', 'fast', 'tank'], weights=[70, 20, 10])[0]
        hp, speed, damage = self.difficulty_manager.get_zombie_stats(self.current_wave, z_type)
        
        if z_type == 'normal': zombie = NormalZombie(x, y)
        elif z_type == 'fast': zombie = FastZombie(x, y)
        else: zombie = TankZombie(x, y)
            
        zombie.hp = hp
        zombie.speed = speed
        zombie.attack_damage = damage
        
        self.all_sprites.add(zombie)
        self.zombies.add(zombie)

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            
            if self.game_state == "GAMEOVER":
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if self.restart_button_rect.collidepoint(mouse_pos):
                        self.reset_game()

    def update(self):
        if self.game_state == "PLAYING":
            self.all_sprites.update(player_pos=self.player.rect.center, bullet_group=self.bullets)
            
            for b in self.bullets:
                if b not in self.all_sprites:
                    self.all_sprites.add(b)

            now = pg.time.get_ticks()
            if now - self.spawn_timer > 2000:
                self.spawn_zombie()
                self.spawn_timer = now

            hits = pg.sprite.groupcollide(self.zombies, self.bullets, False, True)
            for zombie, bullets in hits.items():
                for b in bullets:
                    zombie.take_damage(b.damage)
                    if zombie.hp <= 0:
                        self.score += 10

            if pg.sprite.spritecollide(self.player, self.zombies, False):
                for zombie in pg.sprite.spritecollide(self.player, self.zombies, False):
                    zombie.attack(self.player)
                
                if self.player.hp <= 0:
                    self.game_state = "GAMEOVER"

    def draw(self):
        self.screen.fill(DARK_GRAY)
        self.all_sprites.draw(self.screen)
        
        # UI
        ui_font = pg.font.SysFont(None, 36)
        stats_img = ui_font.render(f'HP: {self.player.hp} | Score: {self.score} | Ammo: {self.player.weapon.current_ammo}', True, WHITE)
        self.screen.blit(stats_img, (20, 20))
        
        if self.game_state == "GAMEOVER":
            # Overlay
            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # จอมืดโปร่งแสง
            self.screen.blit(overlay, (0,0))
            
            # Text
            msg = self.font.render("GAME OVER", True, RED)
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
