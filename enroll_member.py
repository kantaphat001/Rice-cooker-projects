"""
enroll_member.py - Windows Helper to Enroll a Family Member's Face on Pi
Usage:
    python enroll_member.py [member_id]
"""

import sys
import os
import time
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

def main():
    print("=" * 70)
    print("   ENROLL FAMILY MEMBER FACE (ระบบบันทึกใบหน้าสมาชิกในบ้าน)")
    print("=" * 70)
    print(" ตัวอย่าง ID สมาชิก:")
    print("   grandpa (คุณตา)")
    print("   grandma (คุณยาย)")
    print("   dad     (คุณพ่อ)")
    print("   mom     (คุณแม่)")
    print("=" * 70)

    if len(sys.argv) > 1:
        member_id = sys.argv[1].strip()
    else:
        try:
            member_id = input("กรุณาระบุ ID สมาชิกที่ต้องการบันทึกใบหน้า: ").strip()
        except EOFError:
            member_id = ""

    if not member_id:
        print("[!] ไม่ได้ระบุ ID ยกเลิกการทำงาน")
        return

    print(f"\n[*] กำลังเชื่อมต่อ Raspberry Pi ({PI_IP})...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] เชื่อมต่อไม่สำเร็จ: {e}")
        return

    print(f"[*] เริ่มขั้นตอนถ่ายภาพใบหน้า 10 ช็อตสำหรับ '{member_id}'...")
    print("    กรุณาให้สมาชิกยืนหน้ากล้อง หันหน้าตรง และเอียงหน้าเล็กน้อย...")

    remote_capture = f"""
python3 -c "
import cv2, os, time
from pathlib import Path

member_dir = Path('/home/pi/smart_rice_cooker/dataset/{member_id}')
member_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print('[-] ไม่สามารถเปิดกล้องได้')
    exit(1)

count = 0
print('[+] กล้องพร้อมแล้ว! กำลังบันทึกภาพ...')
while count < 10:
    ret, frame = cap.read()
    if ret and frame is not None:
        save_path = member_dir / f'face_{{int(time.time()*1000)}}.jpg'
        cv2.imwrite(str(save_path), frame)
        count += 1
        print(f'  [✓] บันทึกภาพที่ {{count}}/10 สำเร็จ: {{save_path.name}}')
        time.sleep(0.4)

cap.release()
print('[+] บันทึกภาพครบ 10 ภาพเรียบร้อย!')
"
"""
    stdin, stdout, stderr = ssh.exec_command(remote_capture)
    for line in iter(stdout.readline, ""):
        print(line, end="")
    err = stderr.read().decode('utf-8', errors='replace').strip()
    if err and "error" in err.lower():
        print("[!] Error:", err)

    print("\n[*] กำลังประมวลผลคำนวณเวกเตอร์ใบหน้า (YuNet + SFace)...")
    stdin, stdout, stderr = ssh.exec_command("cd /home/pi && python3 -m smart_rice_cooker.main --rebuild-faces")
    for line in iter(stdout.readline, ""):
        print(line, end="")

    ssh.close()
    print("\n" + "=" * 70)
    print(f" [+] ลงทะเบียนใบหน้าของ '{member_id}' เข้าสู่ระบบเรียบร้อยแล้ว!")
    print("=" * 70)

if __name__ == "__main__":
    main()
