# Rice Cooker Projects: Raspberry Pi 4 Universal Automated Provisioning Suite

ชุดเครื่องมืออัตโนมัติสำหรับการติดตั้ง กำหนดค่า ปรับจูนประสิทธิภาพระดับเคอร์เนล และควบคุมบอร์ด **Raspberry Pi 4 Model B (Rev 1.5)** ผ่าน Windows แบบ 1-Click

---

## 📌 สเปกและข้อมูลเครื่องเป้าหมายหลัก (Target Profile)
* **IP Address:** `192.168.88.74`
* **MAC Address:** `d8:3a:dd:d4:44:08`
* **Model:** Raspberry Pi 4 Model B Rev 1.5
* **RAM:** 1 GB (~904 MB detected)
* **Default Desktop:** XFCE 4.20 Desktop (หรือสลับเป็น PIXEL / LXDE ได้)
* **Default Credentials:**
  * **User:** `pi`
  * **Password:** `1234`
  * **Sudo:** Passwordless

---

## ⚡ สถาปัตยกรรมและเทคโนโลยีระดับเคอร์เนล (Kernel Optimizations)

1. **In-Memory ZRAM (LZ4 Compression):**
   * ปิดการใช้งาน Swapfile บน MicroSD Card ถาวร (`dphys-swapfile` disabled) เพื่อถนอมอายุการใช้งาน Flash Memory
   * จัดสรรพื้นที่ ZRAM 100% ของขนาด RAM พร้อมอัลกอริทึม LZ4
   * ปรับตั้งค่า `vm.swappiness=100` และ `vm.page-cluster=0` เพื่อลดอาการแล็กจากการสลับหน้าหน่วยความจำ
2. **Dynamic CMA GPU Allocation:**
   * ใช้งานไดรเวอร์เคอร์เนล KMS `vc4-kms-v3d` และยกเลิกการล็อกแรมแบบตายตัว `gpu_mem` เพื่อให้ RAM ทั้งหมดถูกนำมาใช้งานอย่างเต็มประสิทธิภาพ
3. **XRDP & Display Configuration:**
   * บังคับใช้งาน X11 Display Server ป้องกันปัญหาจอดำ และลดข้อขัดแย้งของ DBus เมื่อใช้งานรีโมทพร้อมจอจริง
4. **Modern Python Stack:**
   * ติดตั้งเครื่องมือจัดการแพ็กเกจความเร็วสูง **Astral `uv`**
   * ตั้งค่า `break-system-packages = true` เพื่อรองรับการติดตั้งไลบรารีสากล

---

## 🚀 เครื่องมือควบคุมบน Windows (Control Suite)

| ไฟล์ | ฟังก์ชันการทำงาน |
| :--- | :--- |
| **`Control-Center.bat`** | เปิดศูนย์ควบคุมหลัก 18 เมนู (เรียก PowerShell `Control-Center.ps1`) |
| **`0-Setup-Pi4-Automated.bat`** | ติดตั้งและกำหนดค่าระบบลงบอร์ด `192.168.88.74` อัตโนมัติในคลิกเดียว |
| **`1-Remote-Desktop.bat`** | เปิด Remote Desktop (mstsc.exe) ความละเอียด 1024x600 |
| **`2-SSH-Terminal.bat`** | เปิดหน้าต่าง SSH Console ควบคุมบอร์ดทันที |
| **`3-Switch-OS-Theme.bat`** | สลับหน้าจอระหว่าง **[1] XFCE** (สไตล์ Windows) กับ **[2] PIXEL** (สไตล์ดั้งเดิมของ Pi) |
| **`4-Apply-Optimizations.bat`** | สั่งปรับจูน ZRAM และเคอร์เนลซ้ำได้ตลอดเวลา |
| **`5-Check-System-Health.bat`** | ตรวจสอบอุณหภูมิ CPU, RAM/Swap, พื้นที่ว่าง และสถานะไฟตก (Throttling) |
| **`6-Backup-Pi-Config.bat`** | สำรองไฟล์การตั้งค่าระบบสำคัญเก็บไว้ในโฟลเดอร์ `backups/` บนคอมพิวเตอร์ |

---

## 📂 โครงสร้างสคริปต์บน Raspberry Pi (`pi_setup_scripts/`)

* `master_setup.sh`: ควบคุมลำดับการติดตั้งทั้งหมด
* `01_core_packages.sh`: ติดตั้งไดรเวอร์พื้นฐาน X11, XRDP, เครื่องมือเครือข่าย และสภาพแวดล้อม Python
* `02_setup_xfce.sh`: ติดตั้งและตั้งค่า Desktop XFCE 4.20 สไตล์ Windows (กิน RAM เพียง ~140MB)
* `03_setup_pixel.sh`: ติดตั้ง Desktop PIXEL / LXDE สไตล์ Raspberry Pi ดั้งเดิม (กิน RAM เพียง ~100MB)
* `04_optimizations.sh`: กำหนดค่า ZRAM, sysctl kernel tuning และล้างแคชระบบ
* `05_enable_interfaces.sh`: เปิดใช้งานอินเทอร์เฟซ I2C, SPI, UART, SSH และตั้งค่า Udev Rules สำหรับพอร์ต USB Serial

---

## 📖 ข้อมูลเพิ่มเติมสำหรับ AI Assistants
ดูรายละเอียดบริบทเชิงลึก สเปกฮาร์ดแวร์ และการจูนระดับเคอร์เนลได้ที่ไฟล์ **`AI_SYSTEM_CONTEXT.md`**