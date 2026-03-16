# 🧟‍♂️ Zombie Game NAJA (Pygame)

เกมยิงซอมบี้มุมมองด้านบน (Top-down view) ที่เน้นความสวยงามสไตล์ Modern Neon และระบบการเล่นที่ยืดหยุ่น พัฒนาด้วยภาษา Python และไลบรารี Pygame

---

## 🌟 ฟีเจอร์หลัก (Key Features)

### 🎮 ระบบการเล่นและดีไซน์ (Advanced Gameplay & Design)

- **ระบบ Wave & Spawning**: ซอมบี้จะเกิดเป็นเวฟโดยใช้ระบบ **Queue และ Random Delay** เพื่อให้จังหวะการเกิดดูเป็นธรรมชาติ ไม่ซ้ำซาก
- **โหมดเกม (Game Modes)**: รองรับทั้งโหมด **Story** (ไต่ระดับความยาก) และโหมด **Endless** (ท้าทายขีดจำกัด) ผ่านการใช้ _Strategy Pattern_
- **Premium UI/UX**:
  - ดีไซน์สไตล์ **Neon Glow** พร้อมเอฟเฟกต์ **Pulse** ในหน้าเมนู
  - ระบบ **Glassmorphism Overlay** (เบลอพื้นหลัง) เมื่อกดหยุดเกมหรือเข้าหน้าตั้งค่า
  - **Responsive HUD**: แสดงสถานะ HP, กระสุน, คะแนน และ Wave อย่างชัดเจน
- **การเลือกตัวละครและอาวุธ**: ระบบ Preview ตัวละครแบบเรียลไทม์ และสามารถเลือกติดตั้งอาวุธได้ถึง **2 ชนิด** เพื่อสลับใช้ระหว่างการต่อสู้

### 🔊 ระบบเสียงและตั้งค่า (Dynamic Audio System)

- **Advanced Volume Control**: ระบบตั้งค่าเสียงผ่าน **Sliders** ที่ปรับแยกได้อิสระ (BGM, Shooting, Zombies, Player) ทั้งจากเมาส์และคีย์บอร์ด
- **Sound Priority Management**:
  - **Selective Overlapping**: เสียงยิงและเสียงบาดเจ็บสามารถเล่นซ้อนกันได้เพื่อความมันสะใจ
  - **Mutually Exclusive**: เสียง Reload และ Idle จะถูกจัดการไม่ให้เล่นทับกันจนน่ารำคาญ
  - **Global Stop**: เมื่อเกมจบ เสียงทุกอย่างจะค่อยๆ เงียบลงเพื่อสร้างบรรยากาศ

---

## ⌨️ การควบคุม (Controls)

| การกระทำ                      | ปุ่มควบคุม                              |
| :---------------------------- | :-------------------------------------- |
| **เดิน (Walk)**               | `W` `A` `S` `D`                         |
| **เล็ง (Aim)**                | เลื่อนเมาส์ (Mouse Movement)            |
| **ยิง (Shoot)**               | คลิกเมาส์ซ้าย (Left Click) หรือ `SPACE` |
| **รีโหลด (Reload)**           | กดปุ่ม `R`                              |
| **สลับอาวุธ (Switch Weapon)** | กดปุ่ม `1` หรือ `2`                     |
| **หยุดเกม / ตั้งค่า (Pause)** | กดปุ่ม `ESC`                            |

---

## 🏗️ โครงสร้างโปรเจกต์ (System Architecture)

- **`src/main.py`**: ศูนย์กลางของเกม (Game Loop) การจัดการ State หลัก และการเชื่อมต่อทุกระบบเข้าด้วยกัน
- **`src/game_states.py`**: จัดการ Logic ของแต่ละหน้าจอ (MainMenu, Playing, Settings, etc.) และการเปลี่ยน Scene
- **`src/settings.py`**: ศูนย์รวมค่าคงที่ (Constants) การตั้งค่าปุ่ม และสมดุลของเกม
- **`src/base_entity.py`**: คลาสแม่ (Abstract Class) ของตัวละครที่จัดการเรื่อง Sprite, Physics เบื้องต้น และ Health System
- **`src/player.py` & `src/zombie.py`**: ระบบตัวละครผู้เล่นและซอมบี้ (Normal, Fast, Tank) ที่สืบทอดมาจาก BaseEntity
- **`src/base_weapon.py` & `src/base_bullet.py`**: ระบบ Modular Weaponry ที่ใช้การ Composition ในการสร้างอาวุธ
- **`src/ui_manager.py`**: ระบบ UI Engine สำหรับวาดปุ่ม, สไลเดอร์ และ HUD แบบ Modern Interface
- **`src/sound_component.py`**: ระบบจัดการเสียงแยกตามหมวดหมู่ (Audio System) เพื่อบรรยากาศที่สมจริง
- **`src/wave_difficulty.py`**: ตรรกะการเพิ่มระดับความยากและการกระจายตัวของซอมบี้ (Spawning Logic)

---

## 🚀 วิธีเริ่มใช้งาน

1. **เตรียมสภาพแวดล้อม (Virtual Environment):**
   - **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. **ติดตั้งไลบรารีที่จำเป็น:**

   ```bash
   pip install -r requirements.txt
   ```

3. **รันเกม:**

- **Windows:**
  ```bash
  python src/main.py
  ```
- **macOS/Linux:**
  ```bash
  python3 src/main.py
  ```

---

## 👥 สมาชิกผู้พัฒนา (The Team)

โปรเจกต์นี้ได้รับการพัฒนาโดยแบ่งความรับผิดชอบตามความเชี่ยวชาญ:

1. **นาย ธนวรรธ​ ทองตื้อ**: ผู้ออกแบบ Core Mechanics และระบบฟิสิกส์
   - รับผิดชอบ: `base_entity.py`, `player.py`, `base_weapon.py`, `weapons.py`, `base_bullet.py`, `utils.py`
2. **นาย รัชชานนท์ อรรถพันธ์**: ผู้ออกแบบ UI/UX และระบบ State Machine
   - รับผิดชอบ: `main.py`, `game_states.py`, `settings.py`, `ui_manager.py`, `sound_component.py`, `zombie.py`, `wave_difficulty.py`

---

_Enjoy the Apocalypse!_ 🧟‍♀️🔫
