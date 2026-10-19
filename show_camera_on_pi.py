"""
show_camera_on_pi.py - Launch Live Camera Window on Raspberry Pi's Screen
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

from smart_rice_cooker.utils import get_pi_ip

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"

def main():
    print("=" * 70)
    print("   LAUNCH LIVE CAMERA PREVIEW ON RASPBERRY PI SCREEN")
    print("   (เปิดหน้าต่างแสดงผลกล้องสดบนหน้าจอ Remote Desktop ของ Raspberry Pi)")
    print("=" * 70)
    print(f" Target Box: {PI_USER}@{PI_IP}")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อไปยัง {PI_IP}: {e}")
        return

    # Sync pi_camera_window.py
    sftp = ssh.open_sftp()
    local_script = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "smart_rice_cooker", "tools", "pi_camera_window.py")
    remote_script = "/home/pi/smart_rice_cooker/tools/pi_camera_window.py"
    ssh.exec_command("mkdir -p /home/pi/smart_rice_cooker/tools")
    sftp.put(local_script, remote_script)

    # Also create a .desktop icon on Pi desktop
    desktop_file = """[Desktop Entry]
Name=📷 กล้องตรวจจับใบหน้าสด (Camera Live)
Comment=Live Camera Preview with YuNet Face AI
Exec=python3 /home/pi/smart_rice_cooker/tools/pi_camera_window.py
Icon=camera-video
Terminal=true
Type=Application
Categories=Utility;
"""
    ssh.exec_command("mkdir -p /home/pi/Desktop")
    with sftp.open("/home/pi/Desktop/Camera-Live.desktop", "w") as f:
        f.write(desktop_file)
    ssh.exec_command("chmod +x /home/pi/Desktop/Camera-Live.desktop")
    sftp.close()

    print("[*] กำลังสั่งเปิดหน้าต่างแสดงผลบนหน้าจอ Raspberry Pi...")
    print("----------------------------------------------------------------------")
    print("  กรุณาสลับไปดูที่หน้าต่างโปรแกรม Remote Desktop ของ Raspberry Pi!")
    print("  หน้าต่างแสดงผลกล้องสด (640x480 พร้อมกรอบเขียว AI) จะปรากฏขึ้นที่นั่น")
    print("  กด 'q' บนหน้าต่างกล้อง หรือกด Ctrl+C ที่นี่เมื่อต้องการปิด")
    print("----------------------------------------------------------------------\n")

    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command("python3 /home/pi/smart_rice_cooker/tools/pi_camera_window.py")

    try:
        while True:
            if channel.recv_ready():
                out = channel.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.write(out)
                sys.stdout.flush()
            if channel.recv_stderr_ready():
                err = channel.recv_stderr(4096).decode('utf-8', errors='replace')
                sys.stderr.write(err)
                sys.stderr.flush()
            if channel.exit_status_ready():
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[*] สั่งปิดหน้าต่างกล้อง...")
    finally:
        channel.close()
        ssh.close()
        print("\n[+] สิ้นสุดการทำงาน")

if __name__ == "__main__":
    main()
