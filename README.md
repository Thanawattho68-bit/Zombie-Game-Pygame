# Zombie Survival

โปรเจกต์เกมซอมบี้ 2D มุมมองจากด้านบน (Top-down view) พัฒนาด้วย **Python** และ **Pygame**

## 🎯 เป้าหมายของเกม (Project Scope)

ผู้เล่นต้องควบคุมตัวละครเพื่อกำจัดซอมบี้ที่บุกเข้ามาเป็นระลอก (Wave) เก็บแต้ม (Score) และเอาชีวิตรอดให้นานที่สุด

---

## 🏗️ ระบบสำคัญ (Core Features)

1. **Top-Down Perspective**: มุมมองจากด้านบน สามารถหมุนตัวละครได้ 360 องศาตามเมาส์
2. **Shooting Mechanism**: ยิงกระสุนเพื่อกำจัดซอมบี้
3. **Wave System**: ซอมบี้จะออกมาเป็นฝูง เมื่อกำจัดหมดจะขึ้น Wave ใหม่ที่มีความยากเพิ่มขึ้น
4. **Scoring**: สะสมคะแนนจากการฆ่าซอมบี้และจำนวน Wave ที่รอดชีวิต

---

## 👥 การแบ่งงานสำหรับ 2 คน (Task Distribution)

### **คนที่ 1 (Game Engine & UI)**

- วางโครงสร้างไฟล์โปรเจกต์
- เขียนระบบ Main Loop ของเกม (Update/Draw)
- เขียนระบบ Wave System (ตัวนับรอบ, ตัวสุ่มเกิดซอมบี้)
- เขียนระบบ UI (หน้าจอ Score, หน้าจอก่อนเริ่มเกม, หน้าจอตอนแพ้)
- จัดการไฟล์ assets (เสียง, รูปภาพพื้นหลัง)

### **คนที่ 2 (Gameplay & Mechanics)**

- เขียน Class ของตัวละครหลัก (Player) ระบบเดินและหันตามเมาส์
- เขียน Class ของกระสุน (Bullet) และการยิง
- เขียน Class ของซอมบี้ (Normal, Fast, Tank) และ AI พื้นฐาน (วิ่งเข้าหาผู้เล่น)
- ระบบ Collision (การชน) ของกระสุนกับซอมบี้ และซอมบี้กับผู้เล่น

---

## 🛠️ รายละเอียด Class ตัวละคร (Character Classes)

### 1. **ผู้เล่น**

- **Attributes**: HP, Speed, Attack Speed
- **Behavior**: เคลื่อนที่ด้วย WASD, เล็งด้วยเมาส์, คลิกซ้ายเพื่อยิง

### 2. **ซอมบี้ปกติ**

- **Attributes**: HP (ปานกลาง), Speed (ปานกลาง)
- **Behavior**: เดินตามผู้เล่นอย่างช้าๆ

### 3. **ซอมบี้วิ่งเร็ว**

- **Attributes**: HP (ต่ำ), Speed (สูง)
- **Behavior**: วิ่งเข้าหาผู้เล่นอย่างรวดเร็ว (ตัวสั่นๆ หรือมีเอฟเฟกต์สีที่ต่างออกไป)

### 4. **ซอมบี้ตัวใหญ่**

- **Attributes**: HP (สูงมาก), Speed (ต่ำมาก)
- **Behavior**: อึดและทนทาน ต้องใช้กระสุนหลายนัดในการกำจัด

---

## โครงสร้างโปรเจกต์

```text
Zombie-Game-Pygame/
├── assets/             # เก็บรูปภาพและเสียง
│   ├── sprites/
│   └── sounds/
├── src/                # ซอร์สโค้ด
│   ├── settings.py    # ค่าคงที่ต่างๆ (ความกว้างหน้าจอ, สี, ความเร็ว)
│   ├── sprites.py     # Class ตัวละครทั้งหมด
│   └── main.py        # จุดเริ่มเกม
├── README.md           # คำอธิบายโปรเจกต์
- **requirements.md**: [Requirements Documentation](file:///d:/Work/OOP%20ZOMBIE/Zombie-Game-Pygame/requirements.md)
- **requirements.txt**: [Python dependencies](file:///d:/Work/OOP%20ZOMBIE/Zombie-Game-Pygame/requirements.txt)
```
