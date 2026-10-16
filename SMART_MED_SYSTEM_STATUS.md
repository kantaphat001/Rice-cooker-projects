# Smart Rice Cooker Companion Box - System Architecture & AI Context Specification

> **เอกสารฉบับสมบูรณ์ (2026 Production Edition)**
> จัดทำขึ้นเพื่อให้ AI Assistants (Antigravity, Claude, ChatGPT, Gemini, Cursor) เข้าใจบริบท สถาปัตยกรรม ผังฮาร์ดแวร์ โมดูลโค้ด และสถานะปัจจุบันของระบบอย่างละเอียด 100%

---

## 1. บริบทและแนวคิดของโปรเจกต์ (Project Concept)

ระบบนี้คือ **"กล่องอุปกรณ์เสริมอัจฉริยะ (Companion Box)"** ที่ติดตั้งไว้ข้างหม้อหุงข้าว ทำหน้าที่เป็นผู้ช่วยเตือนการรับประทานยาอัตโนมัติประจำบ้าน โดยเฉพาะสำหรับผู้สูงอายุ (Elderly-Friendly) โดยทำงานอัตโนมัติเต็มรูปแบบโดยที่ผู้ใช้ไม่ต้องกดปุ่มเปิดเครื่องใดๆ (Zero Interaction Onboarding)

* **เป้าหมายหลัก:** ป้องกันการลืมกินยา และป้องกันการกินยาซ้ำ (Zero Overdose / Zero Missed Dose)
* **แพลตฟอร์มฮาร์ดแวร์:** Raspberry Pi 4 Model B Rev 1.5 (IP: `192.168.88.74`, RAM 1GB, aarch64)
* **รูปแบบการติดตั้ง:** กล่องสี่เหลี่ยมติดตั้งด้านข้างหม้อหุงข้าว ห่างจากรูระบายไอน้ำ 30-50 ซม.

---

## 2. ผังการเชื่อมต่อวงจรฮาร์ดแวร์ (Hardware Pinout Mapping)

| อุปกรณ์ | ขาอุปกรณ์ | ขาบน Raspberry Pi 4 (BCM) | Physical Pin | หน้าที่และพฤติกรรมของระบบ |
| :--- | :--- | :--- | :--- | :--- |
| 🔴 **LED สีแดง** | Anode (+) | **GPIO 17** | Pin 11 | **Standby Mode:** ติดค้างเมื่อรอคนเดินมาใกล้ |
| 🟡 **LED สีเหลือง** | Anode (+) | **GPIO 27** | Pin 13 | **Detecting Mode:** ติดสว่างเมื่อ Ultrasonic ปลุกกล้องตรวจจับใบหน้า |
| 🟢 **LED สีเขียว** | Anode (+) | **GPIO 22** | Pin 15 | **Announcing Mode:** ติดค้างเมื่อแจ้งเตือนยา / กะพริบ 2 ครั้งเมื่อทักทายทั่วไป |
| 🔘 **ปุ่มยืนยันกินยา** | Switch Pin | **GPIO 25** | Pin 22 | **Acknowledge Button:** กด 1 ครั้งหลังทานยาเสร็จ (Internal Pull-Up ต่อลง GND Pin 20) |
| 📡 **Ultrasonic TRIG** | Trigger | **GPIO 23** | Pin 16 | ส่งสัญญาณคลื่นเสียงความถี่ 40kHz |
| 📡 **Ultrasonic ECHO** | Echo | **GPIO 24** | Pin 18 | รับสัญญาณสะท้อน *(ผ่านตัวต้านทานแบ่งแรงดัน 1kΩ/2kΩ ดร็อปเหลือ 3.3V)* |
| 📷 **กล้องสแกนหน้า** | USB | **USB 2.0 / 3.0** | พอร์ต USB | ดึงภาพ 2 FPS ใน Standby และ 15 FPS ใน Detecting Mode |
| 🔊 **ลำโพง** | 3.5mm / USB | **Headphone Jack** | Audio Out | เสียงสังเคราะห์ภาษาไทยผ่าน `mpg123` |

---

## 3. สถาปัตยกรรมซอฟต์แวร์แบบโมดูลาร์ (Clean Modular Architecture)

โครงสร้างโฟลเดอร์ถูกแยกออกจากกันอย่างเด็ดขาดตามหลัก Single Responsibility:

```text
Rice-cooker-projects/
├── SMART_MED_SYSTEM_STATUS.md        # [เอกสารนี้] สรุปสถานะและสเปกระบบทั้งหมด
├── med_config.example.json           # ตัวอย่างตารางยาสำหรับ Git
├── med_config.json                   # ฐานข้อมูลยาและสมาชิกครอบครัวจริง (Local only)
├── .gitignore                        # ป้องกันข้อมูลสุขภาพและรูปถ่ายใบหน้าหลุดขึ้น Git
│
├── smart_rice_cooker/                # แพ็กเกจซอฟต์แวร์หลัก
│   ├── main.py                       # CLI Entrypoint รองรับ --gui, --headless, --rebuild-faces
│   ├── service.py                    # Master Orchestrator ประสานงานทุกระบบ
│   │
│   ├── config/                       # ⚙️ การตั้งค่าระบบ
│   │   ├── settings.py               # รวมพิน GPIO, เกณฑ์ระยะทาง, พาธโมเดล
│   │   └── schema.py                 # Pydantic v2 / Dataclass โมเดลตารางยา
│   │
│   ├── core/                         # 🧠 วงจรการทำงานและสื่อสาร
│   │   ├── state_machine.py          # ควบคุม FSM (STANDBY -> DETECTING -> ANNOUNCING)
│   │   └── event_bus.py              # Event Bus แบบ Thread-Safe ด้วย queue.Queue
│   │
│   ├── hardware/                     # 🔌 ตัวขับเคลื่อนอุปกรณ์กายภาพ
│   │   ├── led_controller.py         # คอนโทรลเลอร์ไฟ LED 3 สี (แดง, เหลือง, เขียว)
│   │   ├── ultrasonic_sensor.py      # HC-SR04 พร้อม Median Filter และ Timeout Guard
│   │   ├── button_manager.py         # คอนโทรลเลอร์ปุ่มกด Acknowledge Button
│   │   └── camera_manager.py         # Camera Warm-up Streamer (2 FPS Idle ลดความร้อน)
│   │
│   ├── vision/                       # 👁️ ปัญญาประดิษฐ์ใบหน้า (Edge AI 2026)
│   │   ├── yunet_detector.py         # OpenCV YuNet ONNX (~230KB) ตรวจจับใบหน้า
│   │   ├── sface_recognizer.py       # OpenCV SFace ONNX (~37MB) สกัดเวกเตอร์ 128-D
│   │   └── face_database.py          # ฐานข้อมูลเวกเตอร์สมาชิกครอบครัวและคำนวณ Cosine Similarity
│   │
│   ├── medicine/                     # 💊 ตรรกะการกินยาและป้องกันความผิดพลาด
│   │   ├── repository.py             # โหลดและตรวจสอบ med_config.json
│   │   ├── scheduler.py              # คำนวณมื้อยาปัจจุบัน พร้อมการป้องกันเวลาเพี้ยน (NTP Guard)
│   │   └── adherence_tracker.py      # ระบบติดตามสถานะ Dual-Layer (RAM Disk + SD Card Atomic)
│   │
│   ├── voice/                        # 🔊 ระบบเสียงพูดภาษาไทย
│   │   ├── phrase_builder.py         # ประกอบประโยคภาษาไทยสุภาพ ชัดเจน สไตล์คนแก่
│   │   ├── tts_engine.py             # Edge-TTS (th-TH-PremwadeeNeural) พร้อม MD5 Cache
│   │   ├── audio_player.py           # ควบคุมการเล่นผ่าน mpg123 ป้องกันเสียงซ่า
│   │   └── tts_precompiler.py        # แปลงข้อความล่วงหน้าลง Cache เพื่อทำงานออฟไลน์ 100%
│   │
│   ├── ui/                           # 🖥️ หน้าจอแดชบอร์ด
│   │   └── native_gui.py             # Tkinter Fullscreen GUI ตัวหนังสือยักษ์ (Thread-Safe)
│   │
│   └── models/                       # 📦 โมเดล AI สำเร็จรูป
│       ├── face_detection_yunet_2023mar.onnx
│       └── face_recognition_sface_2021dec.onnx
```

---

## 4. มาตรการความปลอดภัยและป้องกันข้อผิดพลาดทางการแพทย์ (QA Mitigations)

1. **State Confirmation (ไม่ใช้ Cooldown เดาสุ่ม):** การเดินผ่านไม่ได้แปลว่ากินยาแล้ว ระบบจะถือว่ากินยาแล้วเฉพาะเมื่อมีการกดปุ่ม `Acknowledge Button (GPIO 25)` เท่านั้น
2. **Integrated Meal Announcement:** เตือนทั้งยาก่อนอาหารและหลังอาหารในคราวเดียว เนื่องจากผู้สูงอายุเดินมาที่หม้อหุงข้าวคือการเริ่มต้นมื้ออาหาร
3. **Dual-Layer Persistence:** บันทึกสถานะลง RAM Disk (`/dev/shm`) เพื่อความเร็วและถนอม SD Card ควบคู่กับการบันทึกแบบ Atomic ลง `adherence_state.json` บนดิสก์จริง ป้องกันไฟดับแล้วสั่งกินยาซ้ำ
4. **Thermal Management:** กล้องรันเพียง 2 FPS ในโหมด Standby เพื่อป้องกันความร้อนสะสมในกล่องข้างหม้อหุงข้าว
5. **No Static Audio Noise:** บังคับใช้ `mpg123` สำหรับไฟล์ MP3 จาก `edge-tts` เพื่อขจัดเสียงซ่าแสบแก้วหูจาก `aplay`

---

## 5. วิธีการทดสอบและสั่งงานระบบจาก Windows

1. **`7-Start-Companion-Box.bat`:** เริ่มการทำงานของระบบบนบอร์ด Raspberry Pi (`192.168.88.74`) แบบเต็มรูปแบบ (Ultrasonic + Camera + LEDs + Button)
2. **`7-Start-Camera-Only.bat`:** โหมดทดสอบเมื่อต่อเฉพาะกล้อง USB (`--camera-only`) โดยใช้โมเดล YuNet ตรวจจับใบหน้าหน้ากล้องเพื่อปลุกระบบแทน Ultrasonic sensor โดยอัตโนมัติ
3. **`8-Enroll-Family-Face.bat`:** สแกนบันทึกใบหน้าสมาชิกใหม่เข้าสู่โฟลเดอร์ `dataset/<id>` และคำนวณเวกเตอร์ใบหน้า
4. **`9-Hardware-Test-LEDs.bat`:** ทดสอบฮาร์ดแวร์ทีละชิ้นส่วน (ไฟ LED 3 สี, ปุ่มกด, Ultrasonic, และลำโพง)

---

## 6. โหมดเฉพาะกล้อง (Camera-Only Mode / Standalone Vision Wakeup)

เพื่อรองรับการพัฒนาและทดสอบในช่วงที่ยังไม่ได้ต่อ Ultrasonic Sensor หรือไฟ LED กายภาพ ระบบมีโหมด `--camera-only`:
* **Visual Presence Loop:** ใช้ YuNet รันสแกนใบหน้าที่ 2.5 FPS ในโหมด Standby (ใช้ CPU Pi 4 ไม่ถึง 5%)
* **Instant Wakeup:** เมื่อมีคนเดินเข้ามาหน้ากล้องและเห็นใบหน้า ระบบจะเปลี่ยนสถานะเป็น `DETECTING` ทันทีเสมือนมีคลื่นอัลตราโซนิกตรวจจับ
* **Virtual Indicators:** สถานะไฟ LED (แดง/เหลือง/เขียว) จะแสดงผลบนหน้าจอ GUI และแสดงข้อความ Emoji บน Console
* **Virtual Acknowledge:** ปุ่มยืนยันการทานยาจะปรากฏบนหน้าจอ Tkinter หรือพิมพ์ปุ่มคำสั่งในคอนโซลได้โดยไม่ต้องพึ่งพาสวิตช์ฮาร์ดแวร์ GPIO 25

---

## 7. ผลการทดสอบระบบจริงบน Raspberry Pi (Production Verification)

* **OpenCV Version:** `4.10.0` (ผ่านการทดสอบโหลดโมเดล YuNet และ SFace ได้อย่างสมบูรณ์)
* **Pydantic Version:** `2.10.6` (โหลดสคีมาตารางยา `med_config.json` ถูกต้อง)
* **Hardware Camera:** ทดสอบจับภาพจริงที่ `/dev/video0` สำเร็จที่ความละเอียด 640x480 (30 FPS)
* **Edge-TTS & Audio:** สังเคราะห์เสียงภาษาไทย `th-TH-PremwadeeNeural` และบันทึกลงแคชออฟไลน์ได้สำเร็จ 100%
* **Companion Service:** รันโหมด `--camera-only` ทดสอบผ่านฉลุยพร้อมตรวจจับใบหน้าอัตโนมัติ
