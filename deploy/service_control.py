"""
service_control.py - Manage smart-cooker systemd service on Raspberry Pi
"""

import sys
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
    print("   SMART RICE COOKER - SERVICE CONTROLLER")
    print("=" * 70)
    print(f" Target Box: {PI_USER}@{PI_IP}")
    print()
    print("  [1] ตรวจสอบสถานะการทำงาน (Check Status & Memory)")
    print("  [2] รีสตาร์ตเซอร์วิส (Restart Service)")
    print("  [3] หยุดการทำงาน (Stop Service)")
    print("  [4] เริ่มการทำงาน (Start Service)")
    print("  [0] ออกจากโปรแกรม")
    print("=" * 70)

    try:
        choice = input("เลือกคำสั่ง (1, 2, 3, 4, 0): ").strip()
    except EOFError:
        choice = "0"

    if choice == "0" or not choice:
        return

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อ {PI_IP}: {e}")
        return

    if choice == "1":
        stdin, stdout, stderr = ssh.exec_command("systemctl status smart-cooker.service --no-pager")
        print("\n" + stdout.read().decode('utf-8', errors='replace').strip())
        stdin, stdout, stderr = ssh.exec_command("free -h; ps aux | grep 'smart_rice_cooker.main' | grep -v grep")
        print("\nMemory:\n" + stdout.read().decode('utf-8', errors='replace').strip())

    elif choice == "2":
        print("\n[*] กำลังรีสตาร์ตเซอร์วิสบน Pi...")
        ssh.exec_command(f"echo {PI_PASS} | sudo -S systemctl restart smart-cooker.service")
        print("[+] สั่งรีสตาร์ตเรียบร้อยแล้ว!")

    elif choice == "3":
        print("\n[*] กำลังหยุดเซอร์วิส...")
        ssh.exec_command(f"echo {PI_PASS} | sudo -S systemctl stop smart-cooker.service")
        print("[+] สั่งหยุดเซอร์วิสเรียบร้อยแล้ว!")

    elif choice == "4":
        print("\n[*] กำลังเริ่มเซอร์วิส...")
        ssh.exec_command(f"echo {PI_PASS} | sudo -S systemctl start smart-cooker.service")
        print("[+] สั่งเริ่มเซอร์วิสเรียบร้อยแล้ว!")

    ssh.close()
    print("\n[+] ดำเนินการสำเร็จ")

if __name__ == "__main__":
    main()
