"""
run_companion_box.py - Automated Runner for Companion Box from Windows
Features:
- Auto SSH & SFTP authentication (no manual password prompt)
- Auto-syncs updated code and configs to Raspberry Pi
- Streams live logs in real-time with full UTF-8 Thai text support
- Interactive Ctrl+C handling to stop remote service cleanly
"""

import sys
import os
import time
import argparse
import io

# Ensure UTF-8 output on Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: 'paramiko' library is required. Please run: pip install paramiko")
    sys.exit(1)

import re
from pc_audio import play_cached_file

PI_IP = "192.168.88.74"
PI_USER = "pi"
PI_PASS = "1234"

def sync_code(ssh):
    print("[*] กำลังตรวจสอบและซิงค์โค้ดไปยัง Raspberry Pi...")
    sftp = ssh.open_sftp()
    local_root = os.path.dirname(os.path.abspath(__file__))
    
    # Sync smart_rice_cooker directory
    for root, dirs, files in os.walk(os.path.join(local_root, "smart_rice_cooker")):
        # Skip pycache, git, dataset, audio_cache
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "dataset", "audio_cache")]
        rel_dir = os.path.relpath(root, local_root).replace("\\", "/")
        remote_dir = f"/home/{PI_USER}/{rel_dir}"
        
        try:
            sftp.stat(remote_dir)
        except IOError:
            ssh.exec_command(f"mkdir -p {remote_dir}")
            
        for file in files:
            if file.endswith((".py", ".json", ".txt")) and not file.endswith(".pyc"):
                loc_file = os.path.join(root, file)
                rem_file = f"{remote_dir}/{file}"
                sftp.put(loc_file, rem_file)

    # Sync config if exists
    cfg = os.path.join(local_root, "med_config.json")
    if os.path.exists(cfg):
        sftp.put(cfg, f"/home/{PI_USER}/med_config.json")
        
    sftp.close()
    print("[+] ซิงค์ไฟล์ล่าสุดสำเร็จเรียบร้อยแล้ว!")

def main():
    parser = argparse.ArgumentParser(description="Smart Rice Cooker Windows Runner")
    parser.add_argument("--camera-only", action="store_true", default=True, help="Run in Camera-Only mode (default)")
    parser.add_argument("--full-hardware", action="store_true", help="Enable Ultrasonic & physical LEDs")
    parser.add_argument("--gui", action="store_true", help="Launch GUI on Pi screen")
    args, unknown = parser.parse_known_args()

    mode_flag = "--camera-only"
    if args.full_hardware:
        mode_flag = ""

    print("=" * 70)
    print("   SMART RICE COOKER COMPANION BOX (2026 EDITION) - RUNNER")
    print("=" * 70)
    print(f" Target IP: {PI_IP} (User: {PI_USER})")
    print(f" Mode     : {'Camera-Only Mode (ต่อเฉพาะกล้อง USB)' if mode_flag else 'Full Hardware Mode'}")
    print("=" * 70)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        print(f"[*] กำลังเชื่อมต่อ SSH ไปยัง {PI_IP}...")
        ssh.connect(PI_IP, username=PI_USER, password=PI_PASS, timeout=8)
        print("[+] เชื่อมต่อสำเร็จ!")
    except Exception as e:
        print(f"[!] ไม่สามารถเชื่อมต่อไปยัง {PI_IP}: {e}")
        return

    try:
        sync_code(ssh)
    except Exception as e:
        print(f"[!] Warning: sync code failed ({e}), continuing with existing files...")

    # Auto-pause background service to free camera and GPIO
    service_was_running = False
    try:
        stdin, stdout, stderr = ssh.exec_command("systemctl is-active smart-cooker.service")
        if stdout.read().decode().strip() == "active":
            print("[*] กำลังหยุด background service ชั่วคราวเพื่อปลดล็อกกล้องและ GPIO...")
            ssh.exec_command("sudo systemctl stop smart-cooker.service")
            service_was_running = True
            time.sleep(1.0)
    except Exception:
        pass

    remote_cmd = f"cd /home/{PI_USER} && python3 -m smart_rice_cooker.main --headless {mode_flag}"
    print(f"\n[*] กำลังสั่งรัน: {remote_cmd}")
    print("-" * 70)
    print("  ระบบกำลังทำงาน... กด Ctrl+C เพื่อหยุดโปรแกรม")
    print("-" * 70 + "\n")

    transport = ssh.get_transport()
    channel = transport.open_session()
    channel.get_pty()
    channel.exec_command(remote_cmd)

    sftp = None
    try:
        sftp = ssh.open_sftp()
    except Exception:
        pass

    audio_pattern = re.compile(r'Playing(?:\s+chime)?:\s*([a-zA-Z0-9_\-\.]+?\.mp3)', re.IGNORECASE)
    line_buf = ""

    try:
        while True:
            if channel.recv_ready():
                data = channel.recv(4096).decode('utf-8', errors='replace')
                sys.stdout.write(data)
                sys.stdout.flush()
                line_buf += data
                while "\n" in line_buf:
                    line, line_buf = line_buf.split("\n", 1)
                    m = audio_pattern.search(line)
                    if m:
                        audio_filename = m.group(1)
                        print(f"\n[PC-Speaker] 🔊 กำลังเล่นเสียง '{audio_filename}' ผ่านลำโพงของคอมพิวเตอร์...")
                        play_cached_file(audio_filename, sftp=sftp, blocking=False)
            if channel.recv_stderr_ready():
                err_data = channel.recv_stderr(4096).decode('utf-8', errors='replace')
                sys.stderr.write(err_data)
                sys.stderr.flush()
            if channel.exit_status_ready():
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n\n[*] ผู้ใช้สั่งหยุดระบบ (Ctrl+C)... กำลังปิดเซอร์วิส...")
        channel.close()
    finally:
        if sftp:
            try:
                sftp.close()
            except Exception:
                pass
        if service_was_running:
            print("[*] กำลังเปิด background service กลับคืน...")
            ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
        print("\n[+] ระบบปิดการทำงานเรียบร้อยแล้ว")

if __name__ == "__main__":
    main()
