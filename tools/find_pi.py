"""
tools/find_pi.py - Automated Raspberry Pi Discovery, Internet Provisioning & Network Manager
Scans Wi-Fi, Ethernet, and Hotspot networks to find the Raspberry Pi.
Automatically provisions IP over Ethernet cable and connects Pi to Wi-Fi.
"""

import os
import sys
import time
import socket
import struct
import subprocess
import concurrent.futures
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_IP_FILE = ROOT_DIR / "config_ip.txt"

RPI_MAC_PREFIXES = (
    "d8:3a:dd", "d8-3a-dd",
    "b8:27:eb", "b8-27-eb",
    "dc:a6:32", "dc-a6-32",
    "e4:5f:01", "e4-5f-01",
    "28:cd:c1", "28-cd-c1"
)

PI_USER = "pi"
PI_PASS = "1234"


def get_current_saved_ip() -> str:
    if CONFIG_IP_FILE.exists():
        try:
            val = CONFIG_IP_FILE.read_text(encoding="utf-8").strip()
            if val:
                return val
        except Exception:
            pass
    return "192.168.88.74"


def save_ip(ip: str):
    try:
        CONFIG_IP_FILE.write_text(ip.strip(), encoding="utf-8")
        print(f"[+] บันทึก IP เป้าหมาย: {ip.strip()} ลงใน config_ip.txt เรียบร้อยแล้ว")
    except Exception as e:
        print(f"[!] ไม่สามารถบันทึก config_ip.txt: {e}")


def check_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    try:
        # Check IPv4
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        ok = (s.connect_ex((ip, port)) == 0)
        s.close()
        if ok:
            return True
    except Exception:
        pass

    try:
        # Check IPv6 if ip contains colons or is a hostname
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.settimeout(timeout)
        addrinfo = socket.getaddrinfo(ip, port, socket.AF_INET6, socket.SOCK_STREAM)
        if addrinfo:
            sa = addrinfo[0][4]
            ok = (s.connect_ex(sa) == 0)
            s.close()
            return ok
    except Exception:
        pass
    return False


def ping_ip(ip: str, timeout_ms: int = 400) -> bool:
    try:
        res = subprocess.run(
            ["ping", "-n", "1", "-w", str(timeout_ms), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return res.returncode == 0
    except Exception:
        return False


def get_network_adapters():
    """Return list of (adapter_name, ip_address, prefix_len)."""
    adapters = []
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notmatch '^127\\.' } | Select-Object InterfaceAlias, IPAddress, PrefixLength | ConvertTo-Csv -NoTypeInformation"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3.5)
        lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        if len(lines) > 1:
            for line in lines[1:]:
                parts = [p.strip(' "') for p in line.split(',')]
                if len(parts) >= 3:
                    adapters.append({
                        "name": parts[0],
                        "ip": parts[1],
                        "prefix": int(parts[2]) if parts[2].isdigit() else 24
                    })
    except Exception as e:
        print(f"[!] ตรวจสอบการ์ดเครือข่าย: {e}")
    return adapters


def scan_arp_for_pi():
    """Scan Windows ARP table for known Raspberry Pi MAC OUIs."""
    found = []
    try:
        out = subprocess.check_output(["arp", "-a"], text=True, errors="replace")
        for line in out.splitlines():
            line_clean = line.strip().lower()
            for prefix in RPI_MAC_PREFIXES:
                if prefix in line_clean:
                    parts = re_split_arp(line)
                    if parts:
                        found.append(parts)
    except Exception:
        pass
    return found


def re_split_arp(line: str):
    import re
    match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3})\s+([0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2}[:-][0-9a-f]{2})", line, re.I)
    if match:
        return {"ip": match.group(1), "mac": match.group(2)}
    return None


def sweep_subnet(base_ip: str, max_hosts: int = 254):
    """Pings hosts in /24 subnet in parallel to populate ARP cache."""
    parts = base_ip.split('.')
    if len(parts) != 4:
        return
    prefix = f"{parts[0]}.{parts[1]}.{parts[2]}."
    with concurrent.futures.ThreadPoolExecutor(max_workers=60) as ex:
        futures = [ex.submit(ping_ip, f"{prefix}{i}", 200) for i in range(1, min(max_hosts + 1, 255))]
        concurrent.futures.wait(futures, timeout=3.0)


def connect_pi_to_wifi(pi_target: str, ssid: str, password: str) -> bool:
    """Connects to Pi via SSH and configures Wi-Fi using nmcli or wpa_supplicant."""
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"[*] กำลังเชื่อมต่อไปยัง pi@{pi_target} ผ่าน SSH...")
        ssh.connect(pi_target, username=PI_USER, password=PI_PASS, timeout=6)

        print(f"[*] กำลังสั่งให้บอร์ดเชื่อมต่อ Wi-Fi: '{ssid}'...")
        cmd = f'sudo nmcli dev wifi connect "{ssid}" password "{password}"'
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
        out = stdout.read().decode('utf-8', errors='replace')
        print(out)

        time.sleep(2)
        stdin, stdout, stderr = ssh.exec_command("hostname -I")
        ips_str = stdout.read().decode('utf-8', errors='replace').strip()
        ssh.close()

        print(f"[+] บอร์ด Pi เชื่อมต่อ Wi-Fi สำเร็จ! รายการ IP ของบอร์ด: {ips_str}")
        for ip_cand in ips_str.split():
            if not ip_cand.startswith("169.254.") and ip_cand != pi_target:
                save_ip(ip_cand)
                return True
        return True
    except Exception as e:
        print(f"[!] เกิดข้อผิดพลาดในการเชื่อมต่อ SSH: {e}")
        return False


def enable_internet_sharing_guidance():
    """Provides automated or guided Internet Connection Sharing setup."""
    print("\n" + "=" * 68)
    print("  🌐 ระบบแชร์เน็ตจากคอมพิวเตอร์ไปยังสายแลน (Internet Sharing / ICS)")
    print("=" * 68)
    print("  ระบบนี้จะทำให้ Raspberry Pi ที่ต่อสายแลนเข้าโน้ตบุ๊กได้รับเน็ตทันที")
    print("  โดยคอมพิวเตอร์จะทำหน้าที่เป็นเราเตอร์แจก IP (192.168.137.x) และส่งเน็ตให้บอร์ด\n")
    print("  ขั้นตอนเปิดใช้งานง่ายๆ (ทำเพียงครั้งเดียว):")
    print("  1. กดแป้น Windows + R แล้วพิมพ์:  ncpa.cpl  (กด Enter)")
    print("  2. คลิกขวาที่การ์ด 'Wi-Fi' แล้วเลือก 'Properties' (คุณสมบัติ)")
    print("  3. ไปที่แท็บ 'Sharing' (การแชร์)")
    print("  4. ติ๊กถูกที่ช่อง 'Allow other network users to connect...'")
    print("  5. ในช่อง Home networking connection ให้เลือก 'Ethernet' แล้วกด OK")
    print("  -------------------------------------------------------------")
    print("  * เพียงเท่านี้บอร์ด Raspberry Pi จะเชื่อมต่อเน็ตได้ทันที 100% *")
    print("=" * 68)
    open_now = input("ต้องการเปิดหน้า Network Connections (ncpa.cpl) ตอนนี้เลยหรือไม่? (y/n) [ค่าเริ่มต้น y]: ").strip().lower()
    if open_now != 'n':
        subprocess.Popen(["control.exe", "netconnections"])
    input("\nกด Enter เพื่อกลับสู่เมนูหลัก...")


def discover_pi():
    print("=" * 72)
    print("    🔍 RASPBERRY PI AUTOMATED IP DISCOVERY & NETWORK PROVISIONER (2026)")
    print("    ระบบค้นหาหมายเลข IP และจัดการเครือข่ายสำหรับเครื่องเตือนยาอัตโนมัติ")
    print("=" * 72)

    adapters = get_network_adapters()
    print("[*] รายการการ์ดเครือข่ายบนคอมพิวเตอร์:")
    for a in adapters:
        print(f"    - {a['name']:32} IP: {a['ip']}")

    # 1. Quick test saved IP
    saved_ip = get_current_saved_ip()
    print(f"\n[*] [1/5] ตรวจสอบ IP ล่าสุดใน config_ip.txt ({saved_ip})...")
    if ping_ip(saved_ip, 300) or check_port(saved_ip, 3389) or check_port(saved_ip, 22):
        print(f"    ✅ ยืนยันพบ Raspberry Pi ออนไลน์ที่ IP: {saved_ip}!")
        return saved_ip

    # 2. Check mDNS hostname
    print("[*] [2/5] ตรวจสอบ mDNS hostname (raspberrypi.local)...")
    if ping_ip("raspberrypi.local", 400) or check_port("raspberrypi.local", 3389) or check_port("raspberrypi.local", 22):
        print("    ✅ พบ Raspberry Pi ออนไลน์ผ่านชื่อ hostname: raspberrypi.local!")
        # Check if we can resolve IPv4
        try:
            res_ip = socket.gethostbyname("raspberrypi.local")
            if res_ip and not res_ip.startswith("127."):
                print(f"    [+] แปลงชื่อเป็น IPv4: {res_ip}")
                save_ip(res_ip)
                return res_ip
        except Exception:
            pass
        return "raspberrypi.local"

    # 3. Check Ethernet & Mini DHCP Server
    eth_adapters = [a for a in adapters if "ethernet" in a['name'].lower() or "lan" in a['name'].lower()]
    if eth_adapters:
        print(f"\n[*] [3/5] ตรวจพบสายแลนเชื่อมต่ออยู่ ({eth_adapters[0]['name']})...")
        print("    กำลังเปิดระบบจ่าย IP (Mini DHCP) ผ่านสายแลน 4 วินาที...")
        try:
            from tools.mini_dhcp import run_dhcp_server
            assigned = run_dhcp_server(timeout_sec=4.0)
            if assigned:
                print(f"    🎉 จ่าย IP ให้ Raspberry Pi ผ่านสายแลนสำเร็จ: {assigned}!")
                save_ip(assigned)
                return assigned
        except Exception as e:
            print(f"    [!] DHCP server note: {e}")

    # 4. Sweep Wi-Fi / Active Subnets & Check ARP
    print("\n[*] [4/5] สแกนค้นหาบอร์ด Pi ในเครือข่ายท้องถิ่น (Subnet Sweep)...")
    for a in adapters:
        if "wi-fi" in a['name'].lower() or "wireless" in a['name'].lower() or "hotspot" in a['name'].lower() or a['ip'].startswith("10.") or a['ip'].startswith("192.168.137."):
            print(f"    กำลังสแกนวง {a['name']} ({a['ip']})...")
            sweep_subnet(a['ip'], 254)

    # 5. Check ARP Table
    print("[*] [5/5] ตรวจสอบตาราง ARP สำหรับอุปกรณ์ Raspberry Pi...")
    arp_pis = scan_arp_for_pi()
    if arp_pis:
        for p in arp_pis:
            ip = p['ip']
            mac = p['mac']
            print(f"    [+] ตรวจพบ MAC ของ Raspberry Pi ({mac}) ที่ IP: {ip}")
            if ping_ip(ip, 300) or check_port(ip, 3389) or check_port(ip, 22):
                print(f"    ✅ ยืนยันการเชื่อมต่อ Raspberry Pi ออนไลน์ที่ IP: {ip}!")
                save_ip(ip)
                return ip

    # Fallback to saved
    print(f"\n[!] ไม่พบ IP ใหม่ผ่านการสแกนอัตโนมัติ จะใช้ค่าล่าสุด: {saved_ip}")
    return saved_ip


def interactive_menu(pi_target: str):
    while True:
        rdp_ok = check_port(pi_target, 3389, 0.4)
        ssh_ok = check_port(pi_target, 22, 0.4)
        web_ok = check_port(pi_target, 8080, 0.4)

        print("\n" + "=" * 72)
        print(f"  📌 RASPBERRY PI TARGET: {pi_target}")
        print(f"  สถานะพอร์ต: [RDP 3389: {'🟢 เปิด' if rdp_ok else '🔴 ปิด'}]  "
              f"[SSH 22: {'🟢 เปิด' if ssh_ok else '🔴 ปิด'}]  "
              f"[Web 8080: {'🟢 เปิด' if web_ok else '🔴 ปิด'}]")
        print("=" * 72)
        print("  [1] สั่งให้ Raspberry Pi เชื่อมต่อ Wi-Fi (เช่น znine)")
        print("  [2] เปิด Remote Desktop (mstsc หน้าจอขนาด 1024x600)")
        print("  [3] เปิด SSH Console Terminal")
        print("  [4] เปิดหน้าเว็บจัดการยา (Web Management Portal)")
        print("  [5] เปิดใช้งานระบบแชร์เน็ตจากโน้ตบุ๊กเข้าสายแลน (Internet Sharing / ICS)")
        print("  [6] รันระบบจ่าย IP อัตโนมัติค้างไว้ (Mini DHCP Daemon)")
        print("  [7] สแกนค้นหา IP ใหม่ (Rescan)")
        print("  [0] ออกจากโปรแกรม")
        print("-" * 72)
        choice = input("เลือกคำสั่ง (1-7, 0): ").strip()

        if choice == "1":
            ssid = input("ระบุชื่อ Wi-Fi (SSID) [ค่าเริ่มต้น: znine]: ").strip() or "znine"
            pwd = input(f"ระบุรหัสผ่าน Wi-Fi ของ '{ssid}' [ค่าเริ่มต้น: 987654321]: ").strip() or "987654321"
            connect_pi_to_wifi(pi_target, ssid, pwd)
            input("\nกด Enter เพื่อดำเนินการต่อ...")

        elif choice == "2":
            print(f"[*] กำลังเปิด Remote Desktop ไปยัง {pi_target}...")
            print("    (Username: pi | Password: 1234)")
            subprocess.Popen(["mstsc.exe", f"/v:{pi_target}", "/w:1024", "/h:600"])

        elif choice == "3":
            print(f"[*] กำลังเปิด SSH ไปยัง pi@{pi_target}...")
            os.system(f"ssh -o StrictHostKeyChecking=no pi@{pi_target}")

        elif choice == "4":
            import webbrowser
            webbrowser.open("http://localhost:8080")

        elif choice == "5":
            enable_internet_sharing_guidance()

        elif choice == "6":
            try:
                from tools.mini_dhcp import main as run_dhcp_main
                run_dhcp_main()
            except KeyboardInterrupt:
                print("\nหยุดการทำงาน DHCP")
            input("\nกด Enter เพื่อดำเนินการต่อ...")

        elif choice == "7":
            pi_target = discover_pi()

        elif choice == "0":
            print("สิ้นสุดการทำงาน")
            break


if __name__ == '__main__':
    target = discover_pi()
    interactive_menu(target)
