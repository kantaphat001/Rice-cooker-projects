"""
test_led_direct.py - Direct hardware test to turn ON LEDs and keep them on
"""

import sys
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required")
    sys.exit(1)

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

print("=" * 70)
print("   LED DIRECT HARDWARE TEST (เปิดไฟ LED ค้างไว้เพื่อเช็คการเสียบสาย)")
print("=" * 70)
print(f" Connecting to {PI_USER}@{PI_IP}...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
except Exception as e:
    print(f"[!] เชื่อมต่อไม่สำเร็จ: {e}")
    sys.exit(1)

print("[*] กำลังหยุด smart-cooker.service ชั่วคราว...")
ssh.exec_command("sudo systemctl stop smart-cooker.service")
time.sleep(1)

print("[*] กำลังสั่งเปิดไฟ LED ทั้ง 3 สี (Pin 11, 13, 15) ค้างไว้...")
ssh.exec_command("pinctrl set 17,27,22 op dh")

print("\n" + "=" * 70)
print("  ขณะนี้บอร์ด Raspberry Pi กำลังจ่ายไฟ 3.3V ออกที่พิน:")
print("  - Pin 11 (GPIO 17) -> สำหรับขั้วบวก LED สีแดง")
print("  - Pin 13 (GPIO 27) -> สำหรับขั้วบวก LED สีเหลือง")
print("  - Pin 15 (GPIO 22) -> สำหรับขั้วบวก LED สีเขียว")
print("=" * 70)
print("  [กด Enter เพื่อปิดไฟและออกจากโปรแกรม]")
try:
    input()
except Exception:
    time.sleep(10)

print("[*] กำลังปิดไฟ LED และเปิด service คืนค่าเดิม...")
ssh.exec_command("pinctrl set 17,27,22 op dl")
ssh.exec_command("sudo systemctl start smart-cooker.service")
ssh.close()
print("[+] เสร็จสิ้น")
