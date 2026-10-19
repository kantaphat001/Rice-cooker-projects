"""
view_logs.py - Streams live systemd service logs from Raspberry Pi
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

from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from smart_rice_cooker.utils import get_pi_ip

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"

def main():
    print("=" * 70)
    print("   LIVE SERVICE LOGS - SMART RICE COOKER (RASPBERRY PI)")
    print("=" * 70)
    print(f" Connecting to {PI_USER}@{PI_IP}...")
    print(" กำลังดึง Log สดจากระบบ... กด Ctrl+C เพื่อออก")
    print("-" * 70 + "\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อไปยัง {PI_IP}: {e}")
        return

    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command("journalctl -u smart-cooker -f -n 40 --no-pager")

    try:
        while True:
            if channel.recv_ready():
                out = channel.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.write(out)
                sys.stdout.flush()
            if channel.exit_status_ready():
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[*] ปิดการดู Log")
    finally:
        channel.close()
        ssh.close()

if __name__ == "__main__":
    main()
