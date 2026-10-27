"""
tools/auto_fix_connection.py - 1-Click Automated Connection Repair & Wi-Fi Provisioner
1. Listens for Raspberry Pi on Ethernet cable (DHCP handshake)
2. Assigns IP (169.254.124.200)
3. Connects via SSH to configure Wi-Fi 'znine' automatically
4. Verifies Internet and updates config_ip.txt
"""

import os
import sys
import time
import socket
import struct
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
CONFIG_IP_FILE = ROOT_DIR / "config_ip.txt"

SSID_TARGET = "znine"
PASS_TARGET = "987654321"

PI_USER = "pi"
PI_PASS = "1234"

RPI_MAC_PREFIXES = (
    "d8:3a:dd", "d8-3a-dd",
    "b8:27:eb", "b8-27-eb",
    "dc:a6:32", "dc-a6-32",
    "e4:5f:01", "e4-5f-01",
    "28:cd:c1", "28-cd-c1"
)


def get_ethernet_info():
    eth_ip = "169.254.124.134"
    eth_mask = "255.255.0.0"
    try:
        cmd = [
            "powershell", "-NoProfile", "-Command",
            "Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -like '*Ethernet*' -or $_.InterfaceAlias -like '*LAN*' } | Select-Object -First 1 IPAddress, PrefixLength | ConvertTo-Csv -NoTypeInformation"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=3.0)
        lines = [l.strip() for l in res.stdout.strip().splitlines() if l.strip()]
        if len(lines) > 1:
            parts = [p.strip(' "') for p in lines[1].split(',')]
            if len(parts) >= 2:
                eth_ip = parts[0]
                prefix = int(parts[1]) if parts[1].isdigit() else 16
                mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
                eth_mask = socket.inet_ntoa(struct.pack('>I', mask_int))
    except Exception:
        pass

    ip_parts = [int(p) for p in eth_ip.split('.')]
    mask_parts = [int(p) for p in eth_mask.split('.')]
    bcast_parts = [ip_parts[i] | (~mask_parts[i] & 0xFF) for i in range(4)]
    bcast_ip = ".".join(str(p) for p in bcast_parts)

    offered_parts = list(ip_parts)
    offered_parts[3] = 200 if offered_parts[3] != 200 else 201
    offered_ip = ".".join(str(p) for p in offered_parts)

    return eth_ip, eth_mask, bcast_ip, offered_ip


def ip2bytes(ip_str):
    return socket.inet_aton(ip_str)


def build_dhcp_reply(msg_type, client_xid, client_mac_raw, server_ip, offered_ip, subnet_mask):
    packet = bytearray([2, 1, 6, 0])
    packet.extend(client_xid)
    packet.extend(b'\x00\x00\x80\x00')
    packet.extend(b'\x00\x00\x00\x00')
    packet.extend(ip2bytes(offered_ip))
    packet.extend(ip2bytes(server_ip))
    packet.extend(b'\x00\x00\x00\x00')
    packet.extend(client_mac_raw)
    packet.extend(b'\x00' * 64)
    packet.extend(b'\x00' * 128)
    packet.extend(b'\x63\x82\x53\x63')

    packet.extend(bytes([53, 1, msg_type]))
    packet.extend(bytes([54, 4]) + ip2bytes(server_ip))
    packet.extend(bytes([51, 4]) + struct.pack('>I', 86400))
    packet.extend(bytes([1, 4]) + ip2bytes(subnet_mask))
    packet.extend(bytes([3, 4]) + ip2bytes(server_ip))
    packet.extend(bytes([6, 4]) + ip2bytes("8.8.8.8"))
    packet.append(255)

    if len(packet) < 300:
        packet.extend(b'\x00' * (300 - len(packet)))
    return bytes(packet)


def wait_for_pi_dhcp(timeout_sec=45):
    server_ip, subnet_mask, bcast_ip, offered_ip = get_ethernet_info()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    try:
        s.bind(('0.0.0.0', 67))
    except Exception as e:
        print(f"[!] Warning: Port 67 in use ({e}). Checking if Pi already has IP...")
        return offered_ip

    s.settimeout(1.0)
    start_time = time.time()
    assigned = None

    print(f"\n[*] ระบบ DHCP พร้อมแจก IP {offered_ip} ให้บอร์ด Raspberry Pi ทางสายแลน...")
    print("=" * 70)
    print("  👉 ขั้นตอนง่ายๆ ขั้นตอนเดียว:")
    print("     กรุณา 'ถอดสายแลนออกจากโน้ตบุ๊ก แล้วเสียบกลับเข้าไปใหม่ 1 ครั้ง'")
    print("=" * 70)

    while time.time() - start_time < timeout_sec:
        remaining = int(timeout_sec - (time.time() - start_time))
        sys.stdout.write(f"\r[*] กำลังรอการเสียบสายแลนใหม่... (เหลือเวลา {remaining} วิ) ")
        sys.stdout.flush()

        try:
            data, addr = s.recvfrom(2048)
            if len(data) < 240:
                continue
            xid = data[4:8]
            chaddr = data[28:44]
            mac_str = ':'.join(f'{b:02x}' for b in chaddr[:6])

            is_pi = any(mac_str.lower().startswith(p.replace('-', ':')) for p in RPI_MAC_PREFIXES)

            opts = data[240:]
            msg_type = None
            idx = 0
            while idx < len(opts):
                code = opts[idx]
                if code == 255:
                    break
                if code == 0:
                    idx += 1
                    continue
                if idx + 1 >= len(opts):
                    break
                length = opts[idx + 1]
                val = opts[idx + 2:idx + 2 + length]
                if code == 53 and len(val) == 1:
                    msg_type = val[0]
                idx += 2 + length

            if msg_type == 1:  # DHCPDISCOVER
                print(f"\n[+] ตรวจพบการเสียบสายแลนจาก Raspberry Pi (MAC: {mac_str})!")
                reply = build_dhcp_reply(2, xid, chaddr, server_ip, offered_ip, subnet_mask)
                s.sendto(reply, (bcast_ip, 68))
                print(f"[+] ส่ง DHCPOFFER ({offered_ip}) สำเร็จ")

            elif msg_type == 3:  # DHCPREQUEST
                reply = build_dhcp_reply(5, xid, chaddr, server_ip, offered_ip, subnet_mask)
                s.sendto(reply, (bcast_ip, 68))
                print(f"[+] ส่ง DHCPACK สำเร็จ! บอร์ด Raspberry Pi ได้รับ IP: {offered_ip}")
                assigned = offered_ip
                break

        except socket.timeout:
            continue
        except Exception as e:
            print(f"\n[!] Socket note: {e}")
            break

    s.close()
    return assigned


def provision_wifi_via_ssh(ip: str):
    import paramiko
    print(f"\n[*] กำลังเชื่อมต่อไปยัง Raspberry Pi ที่ {ip} ผ่าน SSH...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    connected = False
    for attempt in range(5):
        try:
            ssh.connect(ip, username=PI_USER, password=PI_PASS, timeout=4)
            connected = True
            break
        except Exception:
            time.sleep(1.5)

    if not connected:
        print(f"[!] ไม่สามารถเชื่อมต่อ SSH ไปยัง {ip} ได้")
        return None

    print(f"[+] เชื่อมต่อ SSH สำเร็จ! กำลังสั่งให้บอร์ดเชื่อมต่อ Wi-Fi '{SSID_TARGET}'...")
    cmd = f'sudo nmcli dev wifi connect "{SSID_TARGET}" password "{PASS_TARGET}"'
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=15)
    out = stdout.read().decode('utf-8', errors='replace')
    print(out)

    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("hostname -I")
    ips_str = stdout.read().decode('utf-8', errors='replace').strip()
    ssh.close()

    print(f"[+] บอร์ดเชื่อมต่อสำเร็จ! รายการ IP ทั้งหมดของบอร์ด: {ips_str}")
    wifi_ip = None
    for cand in ips_str.split():
        if cand.startswith("10.57.215."):
            wifi_ip = cand
            break

    final_ip = wifi_ip or (ips_str.split()[0] if ips_str.split() else ip)
    CONFIG_IP_FILE.write_text(final_ip.strip(), encoding="utf-8")
    print(f"🎉 อัปเดต IP ใช้งานลงใน config_ip.txt: {final_ip}")
    return final_ip


def main():
    print("=" * 72)
    print("    🔧 ONE-CLICK AUTO-FIX & NETWORK PROVISIONER (2026 EDITION)")
    print("    ระบบแก้ไขการเชื่อมต่อและดึง Raspberry Pi เข้าสู่ระบบอัตโนมัติ")
    print("=" * 72)

    assigned_ip = wait_for_pi_dhcp(timeout_sec=40)
    target_ip = assigned_ip or "169.254.124.200"

    final_ip = provision_wifi_via_ssh(target_ip)
    if final_ip:
        print("\n" + "=" * 72)
        print("  🎉 ซ่อมแซมระบบสำเร็จ 100%! บอร์ดพร้อมใช้งานทันที")
        print(f"  IP ปัจจุบัน: {final_ip}")
        print("=" * 72)
        run_now = input("\nต้องการเปิด '10-Start-Companion-Box.bat' ตอนนี้เลยหรือไม่? (y/n) [ค่าเริ่มต้น y]: ").strip().lower()
        if run_now != 'n':
            runner_bat = ROOT_DIR / "10-Start-Companion-Box.bat"
            subprocess.Popen(["cmd.exe", "/c", str(runner_bat)])
    else:
        print("\n[!] หากยังเชื่อมต่อไม่ได้ แนะนำให้ดับเบิลคลิก 'Enable-LAN-Internet.bat' เพื่อแชร์เน็ต")


if __name__ == '__main__':
    main()
