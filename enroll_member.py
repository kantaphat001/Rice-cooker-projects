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

def pause_service_if_active(ssh):
    stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service")
    status = stdout.read().decode('utf-8', errors='replace').strip()
    if status == "active":
        print("[*] กำลังหยุด smart-cooker.service ชั่วคราวเพื่อปลดล็อกกล้อง...")
        ssh.exec_command("sudo systemctl stop smart-cooker.service")
        time.sleep(1.0)
        return True
    return False

def resume_service(ssh):
    print("[*] กำลังเปิด smart-cooker.service คืนค่าเดิม...")
    ssh.exec_command("sudo systemctl start smart-cooker.service")

def main():
    print("=" * 70)
    print("   ENROLL FAMILY MEMBER FACE (ระบบบันทึกใบหน้าสมาชิกในบ้าน)")
    print("=" * 70)
    print(" ตัวอย่าง ID สมาชิกที่ตั้งไว้ใน med_config.json:")
    print("   grandpa (คุณตา)")
    print("   grandma (คุณยาย)")
    print("   หรือระบุ ID อื่นๆ เพื่อเพิ่มสมาชิกใหม่")
    print("=" * 70)

    if len(sys.argv) > 1:
        member_id = sys.argv[1].strip()
    else:
        try:
            member_id = input("กรุณาระบุ ID สมาชิกที่ต้องการบันทึกใบหน้า (เช่น grandpa): ").strip()
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

    was_paused = False
    try:
        was_paused = pause_service_if_active(ssh)

        print(f"\n[*] เริ่มขั้นตอนถ่ายภาพใบหน้า 10 ภาพสำหรับ '{member_id}'...")
        print("    👉 กรุณายืนหน้ากล้อง หันหน้าตรง และขยับเอียงหน้าเล็กน้อยเพื่อความแม่นยำ...")

        remote_capture = f"""
python3 -c "
import cv2, os, time
from pathlib import Path

member_dir = Path('/home/pi/dataset/{member_id}')
member_dir.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
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
            print("[!] Warning/Error:", err)

        print("\n[*] กำลังประมวลผลคำนวณเวกเตอร์ใบหน้า (AI YuNet + SFace)...")
        stdin, stdout, stderr = ssh.exec_command("cd /home/pi && python3 -m smart_rice_cooker.main --rebuild-faces")
        for line in iter(stdout.readline, ""):
            print(line, end="")

        # Sync photos back to local Windows folder if desired
        try:
            sftp = ssh.open_sftp()
            local_member_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", member_id)
            os.makedirs(local_member_dir, exist_ok=True)
            remote_files = sftp.listdir(f"/home/pi/dataset/{member_id}")
            for rf in remote_files:
                if rf.endswith((".jpg", ".png")):
                    sftp.get(f"/home/pi/dataset/{member_id}/{rf}", os.path.join(local_member_dir, rf))
            sftp.close()
            print(f"[+] ซิงค์รูปภาพใบหน้าลงเครื่องคอมพิวเตอร์เรียบร้อย: dataset/{member_id}/")
        except Exception:
            pass

    finally:
        if was_paused:
            resume_service(ssh)
        ssh.close()

    print("\n" + "=" * 70)
    print(f" [+] ลงทะเบียนใบหน้าของ '{member_id}' เข้าสู่ระบบเรียบร้อยแล้ว!")
    print("=" * 70)

if __name__ == "__main__":
    main()
