"""
view_live_camera.py - Start Live Camera Stream on Pi and Open Browser on Windows
"""

import sys
import os
import time
import webbrowser
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

from smart_rice_cooker.utils import get_pi_ip

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"
PORT = 8080

def main():
    print("=" * 70)
    print("   SMART RICE COOKER - LIVE CAMERA STREAM VIEWER")
    print("=" * 70)
    print(f" Target Box: {PI_USER}@{PI_IP}")
    print(" กำลังเริ่มระบบสตรีมภาพกล้องสด + AI ตรวจจับใบหน้า (YuNet)...")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] เชื่อมต่อ Pi ไม่สำเร็จ: {e}")
        return

    # Sync camera_stream_server.py
    sftp = ssh.open_sftp()
    local_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smart_rice_cooker", "tools", "camera_stream_server.py")
    remote_script = "/home/pi/smart_rice_cooker/tools/camera_stream_server.py"
    
    # Ensure remote directory exists
    ssh.exec_command("mkdir -p /home/pi/smart_rice_cooker/tools")
    sftp.put(local_script, remote_script)
    sftp.close()

    print("[*] กำลังเปิดเซิร์ฟเวอร์สตรีมภาพบน Raspberry Pi...")
    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command(f"cd /home/pi && python3 -m smart_rice_cooker.tools.camera_stream_server")

    time.sleep(2)

    url = f"http://{PI_IP}:{PORT}/"
    print(f"\n[+] กำลังเปิดเบราว์เซอร์ไปที่: {url}")
    print("-" * 70)
    print("  กำลังสตรีมภาพวิดีโอสดเข้าสู่เบราว์เซอร์ของคุณ...")
    print("  กด Ctrl+C ที่หน้าต่างนี้เมื่อต้องการปิดการสตรีม")
    print("-" * 70 + "\n")
    webbrowser.open(url)

    try:
        while True:
            if channel.recv_ready():
                out = channel.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.write(out)
                sys.stdout.flush()
            if channel.exit_status_ready():
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n[*] ผู้ใช้สั่งปิดสตรีมกล้อง...")
    finally:
        channel.close()
        # Kill python process on port 8080 if lingering
        ssh.exec_command("pkill -f camera_stream_server")
        ssh.close()
        print("[+] ปิดระบบสตรีมกล้องเรียบร้อยแล้ว")

if __name__ == "__main__":
    main()
