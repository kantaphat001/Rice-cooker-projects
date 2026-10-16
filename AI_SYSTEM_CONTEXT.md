# Raspberry Pi 4 - Automated Setup and Dual-OS System Specification

เอกสารฉบับนี้จัดทำขึ้นเพื่อให้ AI Assistant (Antigravity, Cursor, Claude, ChatGPT, Gemini) เข้าใจบริบท สเปกฮาร์ดแวร์ โครงสร้างโปรไฟล์ และสถานะปัจจุบันของระบบอย่างละเอียด 100%

---

## 1. ข้อมูลฮาร์ดแวร์และโปรไฟล์เครื่องเป้าหมาย (Hardware and Target Profile)

ระบบกำหนดเป้าหมายหลักไปที่บอร์ด Raspberry Pi 4 ของผู้ใช้โดยตรง:

### เครื่องหลัก (Primary Device):
* IP Address: 192.168.88.74
* MAC Address: d8:3a:dd:d4:44:08
* Model: Raspberry Pi 4 Model B Rev 1.5
* RAM: 1 GB (~904 MB detected)
* Active Desktop Style: XFCE 4.20 Desktop (หรือ PIXEL สลับได้ตามต้องการ)
  * สไตล์เสมือน Windows ดั้งเดิม
  * Start Menu มุมซ้ายล่าง, Taskbar ล่าง, ตัวจัดการไฟล์ Thunar
  * กิน RAM ต่ำมากเพียง ~130-150 MB (เหมาะอย่างยิ่งสำหรับบอร์ด 1GB)
* Default Credentials: User: pi | Password: 1234 | Sudo: Passwordless

*(หมายเหตุ: ระบบตัดการเชื่อมต่อและไม่สนใจเครื่อง 192.168.88.78 แล้ว โดยกำหนดเป้าหมายหลัก 100% ไปที่ 192.168.88.74)*

---

## 2. การตั้งค่าสถาปัตยกรรมระดับเคอร์เนล (2026 Production Kernel Best Practices)

ชุดเครื่องมือนี้ใช้มาตรฐานการปรับจูนระดับเคอร์เนลยุคใหม่ล่าสุด:

1. In-Memory ZRAM (LZ4 Compression):
   * ปิด Swap บน MicroSD Card ถาวร (dphys-swapfile disabled) เพื่อถนอมอายุการใช้งานของชิป Flash
   * เปิดใช้ ZRAM 100% ของขนาด RAM จริงด้วยอัลกอริทึม lz4 ความเร็วสูง
   * ตั้งค่าเคอร์เนล: vm.swappiness=100 และ vm.page-cluster=0 (บังคับให้เคอร์เนลบีบอัดหน้าความจำใน RAM แทนการทิ้ง Page Cache ของระบบไฟล์)
2. Dynamic CMA GPU Memory Allocation:
   * ไม่ใช้การล็อกแรมแบบตายตัว gpu_mem=128 (เพราะไดรเวอร์เคอร์เนล KMS vc4-kms-v3d ใช้การจัดสรรแรมแบบ Dynamic CMA อยู่แล้ว การล็อกจะทำให้เสีย RAM ฟรีไป 128MB)
3. XRDP and Display Conflict Resolution:
   * บังคับให้ระบบรัน X11 (raspi-config nonint do_wayland W1) เพื่อความเสถียรของ XRDP และจอสัมผัส
   * ใน /etc/xrdp/startwm.sh มีการ unset DBUS_SESSION_BUS_ADDRESS และ unset XDG_RUNTIME_DIR เพื่อให้สามารถเปิดจอ HDMI และรีโมท XRDP พร้อมกันได้โดยไม่เกิดปัญหาจอดำ
4. Modern Python Ecosystem:
   * ติดตั้ง Astral uv สำหรับการจัดการแพ็กเกจความเร็วสูง
   * กำหนดค่า break-system-packages = true ใน /etc/pip.conf เพื่อป้องกัน Error PEP 668 เมื่อต้องการติดตั้งไลบรารีสากล

---

## 3. สรุปรายการไฟล์ในชุดเครื่องมือ Windows

1. Control-Center.bat: เปิดศูนย์ควบคุมหลักแบบเต็มรูปแบบ 18 เมนู (เรียก Control-Center.ps1)
2. 0-Setup-Pi4-Automated.bat: สคริปต์ติดตั้งอัตโนมัติ 1 คลิกจาก Windows โดยส่งสคริปต์ผ่าน SCP และรัน Master Setup
3. 1-Remote-Desktop.bat: เปิดหน้าจอ Remote Desktop 1024x600 ไปยัง IP เป้าหมาย
4. 2-SSH-Terminal.bat: เปิดคอนโซล SSH Terminal ควบคุมบอร์ด
5. 3-Switch-OS-Theme.bat: สลับหน้าจอระหว่าง [1] XFCE (สไตล์ Windows) กับ [2] PIXEL (สไตล์ Raspberry Pi)
6. 4-Apply-Optimizations.bat: สั่งรันชุดจูนเคอร์เนล ZRAM และระบบแคชซ้ำได้ตลอดเวลา
7. 5-Check-System-Health.bat: แสดงความร้อน CPU, RAM, Swap, Disk และสถานะไฟตก (Throttling)
8. 6-Backup-Pi-Config.bat: สำรองไฟล์คอนฟิกสำคัญของ Pi เก็บลงโฟลเดอร์ backups บนคอมพิวเตอร์
