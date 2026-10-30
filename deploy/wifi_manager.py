"""
wifi_manager.py - Raspberry Pi Wi-Fi Network Manager
Manage, scan, and save Wi-Fi networks on Raspberry Pi.
Supports Dual-Mode:
- When running natively on Raspberry Pi (e.g. from web manager or CLI on Pi):
  Executes NetworkManager CLI (`nmcli`) locally via subprocess with zero dependencies (no paramiko required).
- When running remotely on PC:
  Executes via SSH using paramiko.
"""

import os
import sys
import time
import socket
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

PI_USER = "pi"
PI_PASS = "1234"

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


def is_running_on_pi() -> bool:
    """Check if running natively on Raspberry Pi."""
    try:
        if Path("/home/pi").is_dir():
            return socket.gethostname() == "raspberrypi" or str(ROOT_DIR).startswith("/home/pi")
    except Exception:
        pass
    return False


def _get_ssh():
    """Establish SSH connection to Raspberry Pi when running from PC."""
    if not PARAMIKO_AVAILABLE:
        raise RuntimeError("Paramiko is not installed on PC. Please run: pip install paramiko")
    try:
        from web.backend.network_utils import get_pi_ip
    except ImportError:
        from smart_rice_cooker.utils import get_pi_ip
    ip = get_pi_ip()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=6)
    return ssh


def _exec_command(cmd: str, timeout: int = 25) -> Tuple[bool, str, str]:
    """
    Execute a shell command either locally on Pi or remotely via SSH.
    Returns (success, stdout, stderr).
    """
    if is_running_on_pi():
        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate(input=f"{PI_PASS}\n", timeout=timeout)
            return (proc.returncode == 0, stdout.strip(), stderr.strip())
        except subprocess.TimeoutExpired:
            proc.kill()
            return (False, "", "Command timed out")
        except Exception as e:
            return (False, "", str(e))
    else:
        ssh = None
        try:
            ssh = _get_ssh()
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
            if "sudo -S" in cmd:
                stdin.write(f"{PI_PASS}\n")
                stdin.flush()
            out_str = stdout.read().decode('utf-8', errors='replace').strip()
            err_str = stderr.read().decode('utf-8', errors='replace').strip()
            return (True, out_str, err_str)
        except Exception as e:
            return (False, "", str(e))
        finally:
            if ssh:
                try:
                    ssh.close()
                except Exception:
                    pass


def get_current_wifi() -> Optional[str]:
    """Returns the name of the currently connected Wi-Fi or None."""
    try:
        ok, out, _ = _exec_command("nmcli -t -f NAME,DEVICE connection show --active", timeout=5)
        for line in out.splitlines():
            parts = line.split(':')
            if len(parts) >= 2 and parts[1] == 'wlan0':
                return parts[0].strip()
    except Exception as e:
        print(f"[!] Error getting current Wi-Fi: {e}")
    return None


def scan_available_wifi() -> List[Dict]:
    """Scans and returns list of dicts: [{'in_use': bool, 'ssid': str, 'signal': int, 'security': str}]"""
    networks = []
    try:
        # Rescan first with sudo to refresh Wi-Fi cache
        _exec_command("echo 1234 | sudo -S nmcli dev wifi rescan", timeout=8)
        time.sleep(1.2)

        ok, out, err = _exec_command("nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY dev wifi list", timeout=10)
        seen = set()
        for line in out.splitlines():
            parts = line.split(':')
            if len(parts) >= 4:
                in_use = (parts[0].strip() == '*')
                ssid = parts[1].strip()
                if not ssid or ssid in seen:
                    continue
                seen.add(ssid)
                try:
                    signal = int(parts[2].strip())
                except ValueError:
                    signal = 0
                security = parts[3].strip()
                networks.append({
                    "in_use": in_use,
                    "ssid": ssid,
                    "signal": signal,
                    "security": security
                })
        networks.sort(key=lambda x: (not x['in_use'], -x['signal']))
    except Exception as e:
        print(f"[!] Error scanning Wi-Fi: {e}")
    return networks


def list_saved_wifi() -> List[str]:
    """Returns list of saved Wi-Fi connection names."""
    saved = []
    try:
        ok, out, _ = _exec_command("nmcli -t -f NAME,TYPE connection show", timeout=5)
        for line in out.splitlines():
            parts = line.split(':')
            if len(parts) >= 2 and '802-11-wireless' in parts[1]:
                name = parts[0].strip()
                if name and name not in saved:
                    saved.append(name)
    except Exception as e:
        print(f"[!] Error listing saved Wi-Fi: {e}")
    return saved


def add_wifi_network(ssid: str, password: str = "") -> Tuple[bool, str]:
    """Connects to and permanently saves a new Wi-Fi network on the Pi."""
    try:
        if password:
            cmd = f'echo 1234 | sudo -S nmcli dev wifi connect "{ssid}" password "{password}"'
        else:
            cmd = f'echo 1234 | sudo -S nmcli dev wifi connect "{ssid}"'
        ok, out, err = _exec_command(cmd, timeout=30)
        combined = f"{out} {err}".strip()
        success = ("successfully activated" in combined.lower() or "connection successfully" in combined.lower())
        return success, combined or ("เชื่อมต่อสำเร็จ" if success else "ไม่สามารถเชื่อมต่อได้")
    except Exception as e:
        return False, str(e)


def delete_saved_wifi(name: str) -> Tuple[bool, str]:
    """Deletes a saved Wi-Fi profile from the Pi."""
    try:
        cmd = f'echo 1234 | sudo -S nmcli connection delete "{name}"'
        ok, out, err = _exec_command(cmd, timeout=10)
        return ok, out or err
    except Exception as e:
        return False, str(e)


def interactive_menu():
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

    target_ip = get_pi_ip() if not is_running_on_pi() else "localhost (Native Pi)"
    print("=" * 65)
    print("   📶 RASPBERRY PI WI-FI NETWORK MANAGER")
    print("   เครื่องมือจัดการและบันทึก Wi-Fi ล่วงหน้าก่อนย้ายสถานที่")
    print(f"   บอร์ดเป้าหมาย: {target_ip}")
    print("=" * 65)

    current = get_current_wifi()
    print(f" [*] สถานะปัจจุบัน: เชื่อมต่อกับ Wi-Fi -> '{current or 'ไม่พบการเชื่อมต่อ'}'")
    print("-" * 65)
    print(" [1] ดูรายชื่อ Wi-Fi ที่บอร์ด Pi จดจำไว้ทั้งหมด (Saved Networks)")
    print(" [2] สแกนค้นหา Wi-Fi บริเวณใกล้เคียง (Scan Nearby Wi-Fi)")
    print(" [3] เพิ่ม Wi-Fi ใหม่และรหัสผ่าน (เช่น Wi-Fi บ้านใหม่ หรือ Hotspot มือถือ)")
    print(" [4] ลบ Wi-Fi ที่บันทึกไว้ออกจากบอร์ด")
    print(" [5] คำแนะนำการใช้งานเมื่อย้ายเครื่องไปที่อื่น")
    print(" [0] ออกจากโปรแกรม")
    print("=" * 65)

    choice = input("เลือกเมนู (0-5): ").strip()

    if choice == "1":
        saved = list_saved_wifi()
        print("\n=== รายชื่อ Wi-Fi ที่บันทึกไว้ในบอร์ด Pi ===")
        if not saved:
            print(" (ยังไม่มี Wi-Fi บันทึกไว้)")
        for i, s in enumerate(saved, 1):
            tag = " (กำลังใช้งาน)" if s == current else ""
            print(f" {i}. {s}{tag}")

    elif choice == "2":
        print("\n[*] กำลังสแกนคลื่น Wi-Fi รอบๆ บอร์ด Pi (รอสักครู่)...")
        networks = scan_available_wifi()
        print(f"\n=== พบ Wi-Fi ทั้งหมด {len(networks)} เครือข่าย ===")
        print(f" {'สถานะ':<8} {'ชื่อ Wi-Fi (SSID)':<30} {'สัญญาณ':<8} {'ระบบความปลอดภัย'}")
        print("-" * 65)
        for net in networks:
            stat = "🟢 ใช้งาน" if net['in_use'] else "   "
            print(f" {stat:<8} {net['ssid']:<30} {net['signal']}%     {net['security']}")

    elif choice == "3":
        print("\n=== เพิ่ม Wi-Fi ใหม่เข้าบอร์ด Pi ===")
        ssid = input("กรอกชื่อ Wi-Fi (SSID): ").strip()
        if not ssid:
            print("ยกเลิก: ไม่ได้ระบุชื่อ Wi-Fi")
            return
        pwd = input("กรอกรหัสผ่าน Wi-Fi (กด Enter ถ้าไม่มีรหัส): ").strip()
        print(f"\n[*] กำลังส่งคำสั่งบันทึกและเชื่อมต่อไปยัง '{ssid}'...")
        ok, res = add_wifi_network(ssid, pwd)
        if ok:
            print(f"\n[+] สำเร็จ! บอร์ด Pi เชื่อมต่อและจดจำ Wi-Fi '{ssid}' เรียบร้อยแล้ว")
            print("    เมื่อยกกล่องไปสถานที่นี้ บอร์ดจะต่อ Wi-Fi นี้ให้อัตโนมัติ!")
        else:
            print(f"\n[!] ผลลัพธ์: {res}")
            print("    หมายเหตุ: หากยังไม่ได้อยู่ในระยะสัญญาณของ Wi-Fi นี้ ระบบอาจยังเชื่อมต่อไม่ได้")
            print("    แต่ถ้ากรอกชื่อและรหัสผ่านถูกต้อง เมื่อไปถึงที่นั่นให้รีสตาร์ตบอร์ด บอร์ดจะเชื่อมต่อให้อัตโนมัติ")

    elif choice == "4":
        saved = list_saved_wifi()
        print("\n=== เลือกลบ Wi-Fi ออกจากบอร์ด Pi ===")
        for i, s in enumerate(saved, 1):
            print(f" [{i}] {s}")
        idx = input("เลือกหมายเลขที่ต้องการลบ: ").strip()
        try:
            val = int(idx)
            if 1 <= val <= len(saved):
                target = saved[val - 1]
                confirm = input(f"ยืนยันการลบ '{target}' (y/n)? ").strip().lower()
                if confirm == 'y':
                    ok, res = delete_saved_wifi(target)
                    print("[+] ลบสำเร็จ" if ok else f"[!] ผิดพลาด: {res}")
        except Exception:
            print("หมายเลขไม่ถูกต้อง")

    elif choice == "5":
        print("\n=== 💡 คำแนะนำการย้ายเครื่องไปใช้งานที่อื่น ===")
        print(" 1. วิธีที่ดีที่สุด: เพิ่ม Wi-Fi ปลายทางล่วงหน้า")
        print("    - ให้ใช้เมนู [3] เพื่อใส่ชื่อ Wi-Fi และรหัสผ่านของบ้านปลายทางไว้ก่อน")
        print("    - หรือใส่ชื่อและรหัสผ่านของ 'Personal Hotspot มือถือ' ของคุณไว้")
        print(" 2. หากไปถึงที่ใหม่แล้วไม่ได้เพิ่มไว้ล่วงหน้า:")
        print("    - เปิด Hotspot ในมือถือ โดยตั้งชื่อ Wi-Fi (SSID) ให้ตรงกับชื่อ Wi-Fi เดิม")
        print("      (เช่น znine) บอร์ด Pi จะต่อเข้า Hotspot ของคุณทันที!")
        print("    - หรือเสียบสาย LAN เข้ากับเราเตอร์ของบ้านใหม่ จากนั้นเปิดเว็บพอร์ทัลเพื่อตั้งค่า Wi-Fi")
        print(" 3. สคริปต์ทั้งหมดค้นหาบอร์ดผ่าน 'raspberrypi.local' อัตโนมัติ")
        print("    ไม่ว่าเราเตอร์ที่ใหม่จะจ่าย IP อะไร คอมพิวเตอร์จะมองเห็นบอร์ดเสมอ!")


if __name__ == "__main__":
    interactive_menu()
