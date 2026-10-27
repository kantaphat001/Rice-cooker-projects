"""
run_companion_box.py - Automated Runner for Companion Box from Windows
Features:
- Auto SSH & SFTP authentication (no manual password prompt)
- Auto-syncs updated code and configs to Raspberry Pi
- Streams live logs in real-time with full UTF-8 Thai text support
- Interactive Ctrl+C handling to stop remote service cleanly
- Smart fallback connection across LAN, Wi-Fi, and mDNS
- Inline Auto-Fix recovery with zero user friction
"""

import sys
import os
import time
import argparse
import io
from pathlib import Path

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
from smart_rice_cooker.utils import get_pi_ip

ROOT_DIR = Path(__file__).resolve().parent
CONFIG_IP_FILE = ROOT_DIR / "config_ip.txt"

PI_IP = get_pi_ip()
PI_USER = "pi"
PI_PASS = "1234"


def save_active_ip(ip: str):
    try:
        CONFIG_IP_FILE.write_text(ip.strip(), encoding="utf-8")
    except Exception:
        pass


def connect_ssh_with_fallback(primary_ip: str):
    """Attempts connection to primary IP, then tries common fallbacks."""
    candidates = [primary_ip]
    for alt in ["raspberrypi.local", "192.168.137.200", "192.168.88.74", "169.254.124.200"]:
        if alt not in candidates:
            candidates.append(alt)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for ip in candidates:
        try:
            print(f"[*] กำลังเชื่อมต่อ SSH ไปยัง {ip}...")
            ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=3.5)
            print(f"[+] เชื่อมต่อไปยัง {ip} สำเร็จเรียบร้อยแล้ว!")
            if ip != primary_ip:
                save_active_ip(ip)
            return ssh, ip
        except Exception as e:
            print(f"    [-] ไม่สามารถเชื่อมต่อ {ip}: {e}")

    ssh.close()
    return None, None


def sync_code(ssh):
    print("[*] กำลังตรวจสอบและซิงค์โค้ดไปยัง Raspberry Pi...")
    sftp = ssh.open_sftp()
    local_root = os.path.dirname(os.path.abspath(__file__))

    # Sync smart_rice_cooker directory
    for root, dirs, files in os.walk(os.path.join(local_root, "smart_rice_cooker")):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "dataset", "audio_cache")]
        rel_dir = os.path.relpath(root, local_root).replace("\\", "/")
        remote_dir = f"/home/{PI_USER}/{rel_dir}"

        try:
            sftp.stat(remote_dir)
        except IOError:
            _, sout, _ = ssh.exec_command(f"mkdir -p '{remote_dir}'")
            sout.channel.recv_exit_status()

        for file in files:
            if file.endswith((".py", ".json", ".txt")) and not file.endswith(".pyc"):
                loc_file = os.path.join(root, file)
                rem_file = f"{remote_dir}/{file}"
                sftp.put(loc_file, rem_file)

    # Sync config if exists
    cfg = os.path.join(local_root, "med_config.json")
    if os.path.exists(cfg):
        sftp.put(cfg, f"/home/{PI_USER}/med_config.json")

    # Sync audio cache files
    audio_dir = os.path.join(local_root, "audio_cache")
    if os.path.exists(audio_dir):
        _, sout, _ = ssh.exec_command(f"mkdir -p '/home/{PI_USER}/audio_cache'")
        sout.channel.recv_exit_status()
        for f in os.listdir(audio_dir):
            if f.endswith(".mp3"):
                try:
                    sftp.put(os.path.join(audio_dir, f), f"/home/{PI_USER}/audio_cache/{f}")
                except Exception:
                    pass

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

    ssh, connected_ip = connect_ssh_with_fallback(PI_IP)

    if not ssh:
        print("\n" + "=" * 70)
        print(" [!] ไม่สามารถเชื่อมต่อไปยังบอร์ด Raspberry Pi ได้ในขณะนี้")
        print("=" * 70)
        print(" กำลังเปิดระบบซ่อมแซมและดึงบอร์ดเข้าสู่ระบบอัตโนมัติ (Auto-Fix)...")
        try:
            from tools.auto_fix_connection import wait_for_pi_dhcp, provision_wifi_via_ssh
            assigned = wait_for_pi_dhcp(timeout_sec=40)
            target = assigned or "169.254.124.200"
            new_ip = provision_wifi_via_ssh(target)
            if new_ip:
                ssh, connected_ip = connect_ssh_with_fallback(new_ip)
        except Exception as e:
            print(f"[!] Auto-fix note: {e}")

        if not ssh:
            print("\n" + "=" * 70)
            print(" หากยังเชื่อมต่อไม่ได้ แนะนำให้ดับเบิลคลิก 'Enable-LAN-Internet.bat' เพื่อแชร์เน็ต")
            print("=" * 70 + "\n")
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
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\n\n[*] ได้รับคำสั่งหยุด (Ctrl+C)... กำลังปิดโปรแกรมบน Raspberry Pi...")
        channel.close()
    finally:
        if service_was_running:
            print("[*] กำลังเปิด background service กลับคืนสู่สถานะเดิม...")
            ssh.exec_command("sudo systemctl start smart-cooker.service")
        ssh.close()
        print("[+] ปิดการเชื่อมต่อเรียบร้อยแล้ว สวัสดีครับ")


if __name__ == '__main__':
    main()
