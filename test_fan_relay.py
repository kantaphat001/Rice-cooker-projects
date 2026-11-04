"""
test_fan_relay.py - Direct hardware diagnostic test for Cooling Fan Relay
Allows user to test the 5V Relay module and Fan operation on Raspberry Pi.
"""

import sys
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

from smart_rice_cooker.utils import get_pi_ip
from smart_rice_cooker.config import settings

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"
PIN_RELAY = getattr(settings, "PIN_FAN_RELAY", 18)

print("=" * 70)
print("   COOLING FAN RELAY HARDWARE TEST (ทดสอบการทำงานของพัดลมระบายความร้อน)")
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

print(f"\n[*] 1. กำลังสั่งเปิดพัดลมระบายความร้อน (Relay ON ผ่าน Pin 12 / GPIO {PIN_RELAY})...")
# Active Low: pull LOW (dl) to energize relay coil
ssh.exec_command(f"pinctrl set {PIN_RELAY} op dh")
print("  >>> รีเลย์จะส่งเสียง 'คลิก' ไฟสีเขียวบนโมดูลจะติด และพัดลมจะเริ่มหมุน!")

print("\n" + "=" * 70)
print("  [กด Enter เมื่อต้องการทดสอบสั่งปิดพัดลม (จำลองโหมด Eco-Sleep)]")
print("=" * 70)
try:
    input()
except Exception:
    time.sleep(5)

print(f"\n[*] 2. กำลังสั่งปิดพัดลม (Relay OFF ผ่าน Pin 12 / GPIO {PIN_RELAY})...")
# Active Low: pull HIGH (dh) to de-energize relay coil
ssh.exec_command(f"pinctrl set {PIN_RELAY} op dl")
print("  >>> รีเลย์จะคลิกอีกครั้ง ไฟเขียวบนโมดูลดับ และพัดลมหยุดหมุน!")
time.sleep(2)

print("\n[*] กำลังเปิดเซอร์วิสหลัก smart-cooker.service คืนค่าเดิม...")
ssh.exec_command("sudo systemctl start smart-cooker.service")
ssh.close()
print("\n[+] ทดสอบระบบควบคุมพัดลมเสร็จสิ้น 100%!")
