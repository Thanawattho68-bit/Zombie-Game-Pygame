import os
import random
import pygame as pg

def get_random_image(folder_path):
    # ฟังก์ชันช่วยสุ่มไฟล์รูปในโฟลเดอร์ที่กำหนด ถ้ารูปในโฟลเดอร์มีมากกว่า 1 รูป มันจะสุ่มหยิบมา 1 รูป ถ้าโฟลเดอร์ไม่มีอยู่จริง หรือไม่มีรูป จะส่งค่า None กลับไป
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
        if images:
            return os.path.join(folder_path, random.choice(images))
    return None

def load_image(path, size=None, fallback_color=None):
    # โหลดรูปภาพพร้อมจัดการ error และการปรับขนาด (Scale) ถ้าโหลดไม่ได้จะสร้าง Surface สีพื้นสุ่มหรือตามที่กำหนดให้แทน
    if path:
        try:
            img = pg.image.load(path).convert_alpha()
            if size:
                img = pg.transform.scale(img, size)
            return img
        except Exception as e:
            print(f"Warning: Could not load image '{path}' - {e}")
    
    # Logic สำหรับสร้าง Placeholder กรณีไม่มีรูป
    final_size = size if size else (35, 35)
    surface = pg.Surface(final_size)
    
    if fallback_color is None:
        # สุ่มสีถ้าไม่ได้กำหนดมา
        fallback_color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
    
    surface.fill(fallback_color)
    # วาดกรอบสีขาวให้ดูเหมือนบล็อกตัวละคร/ไอเทม
    pg.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
    return surface

def get_direction_vector(start_pos, target_pos):
    # คำนวณ Vector ทิศทางจากจุดหนึ่งไปยังอีกจุดหนึ่ง พร้อม Normalize
    start = pg.math.Vector2(start_pos)
    target = pg.math.Vector2(target_pos)
    direction = target - start
    if direction.length() > 0:
        return direction.normalize()
    return pg.math.Vector2(0, 0)

def draw_text(screen, text, font, color, center_pos):
    # ฟังก์ชันช่วยวาดข้อความให้อยู่กึ่งกลางตำแหน่งที่กำหนด
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=center_pos)
    screen.blit(text_surf, text_rect)
