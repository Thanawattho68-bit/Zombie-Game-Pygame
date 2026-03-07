import os
import random

def get_random_image(folder_path):
    """
    ฟังก์ชันช่วยสุ่มไฟล์รูปในโฟลเดอร์ที่กำหนด
    ถ้ารูปในโฟลเดอร์มีมากกว่า 1 รูป มันจะสุ่มหยิบมา 1 รูป
    ถ้าโฟลเดอร์ไม่มีอยู่จริง หรือไม่มีรูป จะส่งค่า None กลับไป
    """
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        images = [f for f in os.listdir(folder_path) if f.endswith(('.png', '.jpg'))]
        if images:
            return os.path.join(folder_path, random.choice(images))
    return None
