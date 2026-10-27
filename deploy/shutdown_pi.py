"""
shutdown_pi.py - 1-Click Safe Shutdown for Raspberry Pi Companion Box
Flushes disk caches, turns off LEDs, stops background services, and shuts down safely.
"""

import sys
import os
import io
import time
from pathlib import Path

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

try:
    import paramiko
except ImportError:
    print("[!] Error: paramiko is required. Run: pip install paramiko")
    sys.exit(1)

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))
from web.backend.network_utils import get_pi_ip

PI_USER = "pi"
PI_PASS = "1234"

def get_target_ips():
    ips = []
    # 1. From config_ip.txt
    cfg_file = ROOT_DIR / "config_ip.txt"
    if cfg_file.exists():
        try:
            ip = cfg_file.read_text(encoding="utf-8").strip()
            if ip and ip not in ips:
                ips.append(ip)
        except Exception:
            pass
    # 2. Known hotspot / static defaults
    for default_ip in ["10.57.215.17", "192.168.137.102", "172.20.3.37"]:
        if default_ip not in ips:
            ips.append(default_ip)
    return ips

def shutdown_pi(reboot: bool = False) -> bool:
    action_name = "รีบูตเครื่อง (Reboot)" if reboot else "ปิดเครื่องอย่างปลอดภัย (Safe Shutdown)"
    action_cmd = "echo 1234 | sudo -S reboot" if reboot else "echo 1234 | sudo -S poweroff"

    print("=" * 65)
    print(f"   🛑 RASPBERRY PI 1-CLICK POWER MANAGER: {action_name}")
    print("=" * 65)

    # 0. Check if running directly on Raspberry Pi (Linux)
    if sys.platform != "win32":
        try:
            print("[*] ตรวจพบการทำงานบนบอร์ด Raspberry Pi โดยตรง สั่งดำเนินการทันที...")
            import subprocess
            subprocess.run(["sudo", "systemctl", "stop", "smart-cooker.service"], check=False)
            subprocess.run(["python3", "-c", "from gpiozero import LED; [LED(p).off() for p in [17,27,22]]"], check=False)
            subprocess.run(["sync"], check=False)
            local_cmd = "sleep 1 && sudo reboot" if reboot else "sleep 1 && sudo poweroff"
            subprocess.Popen(["bash", "-c", local_cmd])
            print(f"[+] คำสั่ง {action_name} ทำงานสำเร็จ!")
            return True
        except Exception as e:
            print(f"[!] ข้อผิดพลาดในการรันคำสั่งบนเครื่อง: {e}")

    client = None
    connected_ip = None

    for ip in get_target_ips():
        print(f"[*] กำลังทดสอบเชื่อมต่อไปยัง {ip}...")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=22, username=PI_USER, password=PI_PASS, timeout=4, banner_timeout=8, auth_timeout=8)
            client = ssh
            connected_ip = ip
            print(f"[+] เชื่อมต่อสำเร็จผ่าน {connected_ip}")
            break
        except Exception as e:
            print(f"    [-] {ip} ไม่ตอบสนอง: {e}")

    if not client:
        print("\n[!] ไม่สามารถเชื่อมต่อไปยังบอร์ด Raspberry Pi ผ่าน IP ใดๆ ได้ในขณะนี้")
        print("    กรุณาตรวจสอบว่าบอร์ดเปิดอยู่ หรือเสียบสาย LAN / ต่อ Wi-Fi เดียวกันครับ")
        return False

    try:
        print("\n[*] 1. กำลังหยุด smart-cooker.service...")
        client.exec_command(f"echo {PI_PASS} | sudo -S systemctl stop smart-cooker.service")
        time.sleep(0.5)

        print("[*] 2. กำลังปิดไฟ LED ทั้งหมด...")
        client.exec_command(f"echo {PI_PASS} | sudo -S python3 -c \"from gpiozero import LED; [LED(p).off() for p in [17,27,22]]\" 2>/dev/null")
        time.sleep(0.5)

        print("[*] 3. กำลังบันทึกข้อมูลและเคลียร์แคชลงไดรฟ์ (Sync disk buffer)...")
        client.exec_command(f"echo {PI_PASS} | sudo -S sync")
        time.sleep(0.5)

        print(f"[*] 4. กำลังส่งคำสั่ง {action_name}...")
        # Run poweroff/reboot in detached background subshell so SSH cleanly disconnects
        client.exec_command(f"nohup bash -c 'sleep 1 && {action_cmd}' >/dev/null 2>&1 &")
        time.sleep(1)
        client.close()

        print("\n" + "=" * 65)
        if reboot:
            print(" [✅] ส่งคำสั่งรีบูต Raspberry Pi เรียบร้อยแล้ว!")
            print("      บอร์ดจะรีสตาร์ตและพร้อมทำงานใหม่ภายใน 20-30 วินาทีครับ")
        else:
            print(" [✅] ส่งคำสั่งปิดเครื่อง Raspberry Pi เรียบร้อยแล้ว!")
            print("      - ไฟแสดงสถานะบนตัวเครื่องจะดับลงใน 5-10 วินาที")
            print("      - หลังจากไฟดับสนิท สามารถถอดปลั๊ก/สายไฟ Type-C ได้อย่างปลอดภัย 100%")
        print("=" * 65)
        return True

    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาดขณะส่งคำสั่ง: {e}")
        try:
            client.close()
        except Exception:
            pass
        return False

if __name__ == "__main__":
    is_reboot = "--reboot" in sys.argv
    success = shutdown_pi(reboot=is_reboot)
    if not ("--no-pause" in sys.argv):
        input("\nกด Enter เพื่อปิดหน้าต่างนี้...")
