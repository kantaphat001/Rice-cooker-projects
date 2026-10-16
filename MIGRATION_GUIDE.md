# คู่มือการย้ายเครื่องทำงาน (Migration Guide for New PC)
> **บันทึกไว้สำหรับผู้พัฒนา:** นำโค้ดนี้ไปรันหรือพัฒนาต่อบนคอมพิวเตอร์เครื่องใหม่ได้ทันที

---

## 1. ข้อมูลบอร์ด Raspberry Pi ปลายทาง (Target Device)
* **IP Address:** `192.168.88.74` (ต้องต่อ Wi-Fi หรือสาย LAN วงเดียวกันกับคอมพิวเตอร์)
* **SSH Username:** `pi`
* **SSH Password:** `1234`
* **ระบบทำงาน 24/7:** มี Systemd Service ชื่อ `smart-cooker.service` รันอยู่บน Pi อัตโนมัติทุกครั้งที่เสียบปลั๊กไฟ (จำกัด RAM ไม่เกิน 350MB)

---

## 2. ขั้นตอนเตรียมเครื่องใหม่ (Setup New PC)
1. **ติดตั้ง Python:**
   * ดาวน์โหลดและติดตั้ง Python 3.10+ บน Windows (อย่าลืมติ๊กเลือก `Add Python to PATH`)
2. **ติดตั้ง Dependency สำคัญ:**
   เปิด Command Prompt (CMD) หรือ PowerShell แล้วรันคำสั่ง:
   ```bash
   pip install paramiko
   ```
3. **Clone โค้ดจาก GitHub:**
   ```bash
   git clone <URL_ของ_Repository_นี้>
   cd Rice-cooker-projects
   ```

---

## 3. สรุปการจัดระเบียบไฟล์คำสั่ง `.bat` บน Windows

### 💊 ชุดเครื่องมือ Smart Rice Cooker Companion Box (เรียงตามลำดับ 1 - 11):
| ไฟล์ | หน้าที่และการทำงาน |
| :--- | :--- |
| **`1-Install-Autostart-Service.bat`** | ซิงค์โค้ดล่าสุดขึ้น Pi และสั่งเปิด Service 24/7 อัตโนมัติ (รันตัวนี้ตัวแรกเมื่อย้ายเครื่อง) |
| **`2-View-Service-Logs.bat`** | ดู Log การทำงานสดแบบ Real-time (journalctl) |
| **`3-Service-Control.bat`** | ควบคุม Service (Start / Stop / Restart / Status) |
| **`4-System-Monitor.bat`** | แดชบอร์ดมอนิเตอร์ CPU Temp, RAM Usage, Process Memory |
| **`5-Show-Camera-On-Pi.bat`** | เปิดหน้าต่างกล้อง AI บนหน้าจอ Remote Desktop ของ Pi (DISPLAY=:10) |
| **`6-Live-Camera-Stream.bat`** | เปิดดูสตรีมกล้องสดแบบเรียลไทม์ + กล่อง AI ตรวจจับใบหน้าบน Web Browser |
| **`7-Enroll-Family-Face.bat`** | สแกนและลงทะเบียนใบหน้าสมาชิกครอบครัวใหม่เข้าระบบ |
| **`8-Hardware-Diagnostic-Suite.bat`** | ชุดทดสอบฮาร์ดแวร์ทีละชิ้น (LED, Ultrasonic, เสียงลำโพง, ถ่ายภาพกล้อง) |
| **`9-Test-LED-Direct.bat`** | สั่งเปิดไฟ LED 3 สีค้างไว้เพื่อตรวจสอบสายทางกายภาพ |
| **`10-Start-Companion-Box.bat`** | รันระบบเต็มรูปแบบบน Console (แบบเห็น Log สดในหน้าต่าง CMD) |
| **`11-Start-Camera-Only.bat`** | รันโหมดเฉพาะกล้อง USB (จำลองการทำงานโดยไม่ใช้ Ultrasonic) |

### 🖥️ ชุดเครื่องมือดูแลระบบ Raspberry Pi OS:
* **`Pi-Remote-Desktop.bat`**: เปิดรีโมตเดสก์ท็อป (mstsc) ไปยังบอร์ด Pi
* **`Pi-SSH-Terminal.bat`**: เปิดหน้าต่างเทอร์มินัล SSH
* **`Control-Center.bat`**: เมนูควบคุมบอร์ด Pi เต็มรูปแบบ 18 เมนู
* **`Pi-Check-System-Health.bat`**: เช็คความร้อนและสถานะไฟตก

---

## 4. สรุปฮาร์ดแวร์และผังการต่อสาย (Hardware Pinout - ปัจจุบัน)

> **โครงสร้างระบบ:** **Hands-Free ไร้สัมผัส 100% (ไม่มีปุ่มกด)** เมื่อคนเดินมาหน้าหม้อหุงข้าว เซนเซอร์จะวัดระยะ กล้องสแกนหน้า ขานชื่อและเตือนยา จากนั้นจะบันทึกการเตือนและเข้าสู่ช่วง Cooldown โดยอัตโนมัติ

| อุปกรณ์ | ขาอุปกรณ์ | เสียบเข้าพิน Raspberry Pi 4 | Physical Pin | หน้าที่ |
| :--- | :--- | :--- | :--- | :--- |
| 🔴 **LED สีแดง** | ขั้วบวก (+) | **GPIO 17** | **Pin 11** | ไฟสถานะ Standby (ต่อผ่าน R 220Ω-330Ω) |
| 🔴 **LED สีแดง** | ขั้วลบ (-) | **Ground (GND)** | **Pin 9** | กราวด์ไฟแดง |
| 🟡 **LED สีเหลือง** | ขั้วบวก (+) | **GPIO 27** | **Pin 13** | ไฟสถานะ Detecting กำลังสแกนหน้า (ต่อผ่าน R 220Ω-330Ω) |
| 🟡 **LED สีเหลือง** | ขั้วลบ (-) | **Ground (GND)** | **Pin 14** | กราวด์ไฟเหลือง |
| 🟢 **LED สีเขียว** | ขั้วบวก (+) | **GPIO 22** | **Pin 15** | ไฟสถานะ Announcing เตือนยา (ต่อผ่าน R 220Ω-330Ω) |
| 🟢 **LED สีเขียว** | ขั้วลบ (-) | **Ground (GND)** | **Pin 20** | กราวด์ไฟเขียว |
| 📡 **Ultrasonic HC-SR04** | **VCC** | **5V Power** | **Pin 2** | ไฟเลี้ยง 5V |
| 📡 **Ultrasonic HC-SR04** | **GND** | **Ground (GND)** | **Pin 6** | กราวด์เซนเซอร์ |
| 📡 **Ultrasonic HC-SR04** | **TRIG** | **GPIO 23** | **Pin 16** | ขาสั่งยิงคลื่นเสียง |
| 📡 **Ultrasonic HC-SR04** | **ECHO** | **GPIO 24** | **Pin 18** | ขารับคลื่นสะท้อน *(ผ่านตัวแบ่งแรงดัน 1kΩ / 2kΩ ดร็อปเหลือ 3.3V)* |
| 📷 **กล้อง USB** | USB | **USB Port** | **ช่อง USB ใดก็ได้** | สแกนใบหน้าด้วย AI YuNet + SFace |
| 🔊 **ลำโพง** | 3.5mm / USB | **Audio Jack / USB** | **รูแจ็คสีดำ หรือ USB** | เสียงพูดภาษาไทย Edge-TTS ผ่าน `mpg123` |
| 🔘 **ปุ่มกด** | ❌ **ไม่ต้องต่อ** | ❌ **ไม่ใช้งาน** | ❌ **ไม่ใช้งาน** | **ตัดปุ่มออกสมบูรณ์แบบ (Hands-Free)** |

---

## 5. วิธีเริ่มทำงานทันทีบนเครื่องใหม่
1. เสียบสายตามตารางด้านบนให้ครบ
2. ดับเบิลคลิก **`1-Install-Autostart-Service.bat`** เพื่อส่งโค้ดและเริ่มการทำงานบน Pi
3. ดับเบิลคลิก **`8-Hardware-Diagnostic-Suite.bat`** เพื่อทดสอบไฟ LED, เซนเซอร์ Ultrasonic, และเสียงพูด
4. เมื่อใช้งานจริง บอร์ดจะทำงานอัตโนมัติตลอด 24 ชม. ทันทีที่เสียบปลั๊กไฟครับ
