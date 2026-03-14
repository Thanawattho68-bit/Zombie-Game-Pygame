# 🧟‍♂️ Zombie Survival: 2D Top-Down Shooter (Pygame)

เกมยิงซอมบี้มุมมองด้านบน (Top-down view) ที่พัฒนาด้วยภาษา Python และไลบรารี Pygame

---

## 🌟 ฟีเจอร์ที่น่าสนใจ (Key Features)

### 🎮 ระบบการเล่น (Gameplay Structure)

- **ระบบ Wave & Spawning**: ซอมบี้จะเกิดเป็นเวฟ โดยใช้ระบบ **Queue และ Random Delay** เพื่อให้จังหวะการเกิดไม่ซ้ำซากและดูเป็นธรรมชาติ
- **โหมดเกม (Game Modes)**: เลือกเล่นได้ทั้งโหมด **Story** (เพิ่มระดับความยากตามเวฟ) และโหมด **Endless** (ท้าทายความอึด) ผ่านระบบ _Strategy Pattern_
- **การเลือกตัวละคร & อาวุธ**: ก่อนเริ่มแมตช์ ผู้เล่นสามารถเลือกตัวละครที่มี Status ต่างกัน (Soldier, Scout, Defender, Naoya) พร้อมติดตั้งอาวุธที่ชอบได้

### 🔊 ระบบเสียงอัจฉริยะ (Advanced Sound Priority)

เราพัฒนาระบบการลำดับความสำคัญของเสียง (Sound Channels Management) เพื่อประสบการณ์ที่สมจริง:

- **Narrate (เสียงเล่าเรื่อง)**: บทพูดอธิบายที่จะสุ่มเล่นเพียงครั้งเดียวในแมตช์ โดยไม่มีเสียงใดๆ มาขัดจังหวะได้ (ยกเว้นความตาย)
- **World Death Stop**: เมื่อผู้เล่นตาย เสียงทั้งโลกจะหยุดนิ่ง (Global Stop) เพื่อสร้างจังหวะความสลดก่อนเข้าหน้าจอกรรมการ
- **Selective Overlapping**: เสียง **ยิง (Shoot)** และ **บาดเจ็บ (Damage)** สามารถเล่นทับซ้อนกันได้แบบนัวสะใจ แต่เสียง **Idle** และ **Reload** จะสลับกันเล่นอย่างเป็นระเบียบ (Mutually Exclusive)

---

## ⌨️ การควบคุม (Controls)

| การกระทำ            | ปุ่มควบคุม                                           |
| :------------------ | :--------------------------------------------------- |
| **เดิน (Walk)**     | `W` `A` `S` `D`                                      |
| **เล็ง (Aim)**      | เลื่อนเมาส์ (Mouse Movement)                         |
| **ยิง (Shoot)**     | คลิกเมาส์ซ้าย (Left Click) หรือ สเปซบาร์ (Space Bar) |
| **รีโหลด (Reload)** | กดปุ่ม `R`                                           |
| **หยุดเกม (Pause)** | กดปุ่ม `ESC`                                         |

---

## 🏗️ โครงสร้างโปรเจกต์ (System Architecture)

- **`src/main.py`**: ศูนย์กลางการทำงาน (Game Loop, State Machine) และการบริหารจัดการหน้าจอ
- **`src/base_entity.py`**: คลาสแม่สำหรับตัวละครทุกตัว จัดการเรื่อง Logic พื้นฐาน การเคลื่อนที่ และระบบเสียง
- **`src/player.py` / `src/zombie.py`**: แบ่งประเภทตัวละครผู้เล่นและซอมบี้ (Normal, Fast, Tank)
- **`src/base_weapon.py`**: ระบบอาวุธที่ทำงานแบบ Composition ร่วมกับกระสุน (`src/base_bullet.py`)
- **`src/settings.py`**: รวบรวมค่าคงที่ สีสัน และการตั้งค่าปุ่มกดทั้งหมดไว้ในที่เดียว

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
   ```bash
   python src/main.py
   ```

---

## 👥 การแบ่งงาน (Task Distribution)

โปรเจกต์นี้จัดทำโดยสมาชิก 2 คน:

1. **นาย ธนวรรธ​ ทองตื้อ**: ดูแลระบบฟิสิกส์ การเคลื่อนที่ ระบบอาวุธ และการออกแบบตัวละคร
2. **นาย รัชชานนท์ อรรถพันธ์**: ดูแลระบบ Wave, State Machine, ระบบเสียง และ UI/UX

---

_Enjoy the Apocalypse!_ 🧟‍♀️🔫
