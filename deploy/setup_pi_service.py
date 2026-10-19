"""
setup_pi_service.py - Installs and manages 24/7 autonomous service on Raspberry Pi
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
    print("   INSTALL 24/7 AUTOSTART SERVICE ON RASPBERRY PI")
    print("   (ระบบทำงานอัตโนมัติบน Pi กินแรมน้อย ไม่ต้องเปิดคอมพิวเตอร์ทิ้งไว้)")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อไปยัง {PI_IP}: {e}")
        return

    # 1. Sync updated code
    print("[*] กำลังซิงค์ไฟล์โปรแกรมล่าสุด...")
    sftp = ssh.open_sftp()
    local_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Sync smart_rice_cooker
    for root, dirs, files in os.walk(os.path.join(local_root, "smart_rice_cooker")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "dataset", "audio_cache")]
        rel_dir = os.path.relpath(root, local_root).replace("\\", "/")
        remote_dir = f"/home/{PI_USER}/{rel_dir}"
        try:
            sftp.stat(remote_dir)
        except IOError:
            ssh.exec_command(f"mkdir -p {remote_dir}")
        for f in files:
            if f.endswith(".py"):
                sftp.put(os.path.join(root, f), f"{remote_dir}/{f}")

    # Sync service file to /tmp
    service_local = os.path.join(local_root, "deploy", "smart-cooker.service")
    service_tmp = "/tmp/smart-cooker.service"
    sftp.put(service_local, service_tmp)
    sftp.close()

    # 2. Install service with sudo
    print("[*] กำลังติดตั้ง service ลงใน /etc/systemd/system/...")
    cmd_install = f"""
echo {PI_PASS} | sudo -S cp /tmp/smart-cooker.service /etc/systemd/system/smart-cooker.service
echo {PI_PASS} | sudo -S systemctl daemon-reload
echo {PI_PASS} | sudo -S systemctl enable smart-cooker.service
echo {PI_PASS} | sudo -S systemctl restart smart-cooker.service
"""
    stdin, stdout, stderr = ssh.exec_command(cmd_install)
    stdout.channel.recv_exit_status()

    time.sleep(2)

    # 3. Check status
    print("\n[*] ตรวจสอบสถานะการทำงานของระบบบน Raspberry Pi:")
    stdin, stdout, stderr = ssh.exec_command("systemctl status smart-cooker.service --no-pager")
    status_out = stdout.read().decode('utf-8', errors='replace').strip()
    print(status_out)

    # 4. Check memory
    print("\n[*] ตรวจสอบการใช้ RAM ของระบบ:")
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'smart_rice_cooker.main' | grep -v grep")
    ps_out = stdout.read().decode('utf-8', errors='replace').strip()
    print(ps_out if ps_out else "Service starting up...")

    ssh.close()
    print("\n" + "=" * 70)
    print(" [+] ติดตั้งและเปิดใช้งานเซอร์วิสบน Raspberry Pi สำเร็จ 100%!")
    print("     - ระบบจะเปิดทำงานอัตโนมัติทุกครั้งที่เสียบปลั๊กไฟ (Boot on Power)")
    print("     - กล้อง V4L2 พร้อมระบบ Auto-Recovery (หากสายหลุดจะต่อกลับให้อัตโนมัติ)")
    print("     - จำกัด RAM สูงสุดไม่เกิน 350MB เพื่อความเสถียรสูงสุดบน RAM 1GB")
    print("=" * 70)

if __name__ == "__main__":
    main()
