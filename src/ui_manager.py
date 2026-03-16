import pygame as pg
from settings import *

class UIManager:
    def __init__(self, font, btn_font, ui_font):
        self.font = font
        self.btn_font = btn_font
        self.ui_font = ui_font

    def draw_button(self, screen, rect, text, base_color, hover_color, text_color):
        mouse_pos = pg.mouse.get_pos()
        is_hovered = rect.collidepoint(mouse_pos)
        color = hover_color if is_hovered else base_color
        
        # Shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pg.draw.rect(screen, (20, 20, 20), shadow_rect, border_radius=12)
        
        # Button body
        pg.draw.rect(screen, color, rect, border_radius=12)
        pg.draw.rect(screen, WHITE, rect, width=2, border_radius=12)
        
        # Text
        text_surf = self.btn_font.render(text, True, text_color)
        text_rect = text_surf.get_rect(center=rect.center)
        screen.blit(text_surf, text_rect)
        
        return is_hovered

    def draw_slider(self, screen, rect, label, value, is_selected):
        color = PRIMARY_COLOR if is_selected else SECONDARY_COLOR
        
        if is_selected:
            pg.draw.rect(screen, (PRIMARY_COLOR[0]//4, PRIMARY_COLOR[1]//4, PRIMARY_COLOR[2]//4), rect, border_radius=10)
            pg.draw.rect(screen, PRIMARY_COLOR, rect, width=2, border_radius=10)
        else:
            pg.draw.rect(screen, (30, 30, 35), rect, border_radius=10)
        
        # Label
        lbl_surf = self.ui_font.render(label, True, color)
        screen.blit(lbl_surf, lbl_surf.get_rect(midleft=(rect.left + 30, rect.centery)))

        # Slider track
        slider_width = 250
        slider_height = 10
        slider_rect = pg.Rect(0, 0, slider_width, slider_height)
        slider_rect.midleft = (rect.left + 230, rect.centery)
        pg.draw.rect(screen, (60, 60, 65), slider_rect, border_radius=5)

        # Slider handle/fill
        fill_width = int(slider_width * value)
        if fill_width > 0:
            fill_rect = pg.Rect(slider_rect.left, slider_rect.top, fill_width, slider_height)
            pg.draw.rect(screen, color, fill_rect, border_radius=5)
        
        # Handle
        handle_x = slider_rect.left + fill_width
        pg.draw.circle(screen, WHITE, (handle_x, slider_rect.centery), 10)
        pg.draw.circle(screen, color, (handle_x, slider_rect.centery), 8)
