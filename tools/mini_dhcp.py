"""
tools/mini_dhcp.py - Lightweight Dynamic DHCP Server for Raspberry Pi Direct Cable Connection
Automatically discovers the active Ethernet adapter and assigns an IP to the Raspberry Pi.
"""
import os
import sys
import time
import socket
import struct
import subprocess

sys.stdout.reconfigure(encoding='utf-8')

RPI_MAC_PREFIXES = (
    "d8:3a:dd", "d8-3a-dd",
    "b8:27:eb", "b8-27-eb",
    "dc:a6:32", "dc-a6-32",
    "e4:5f:01", "e4-5f-01",
    "28:cd:c1", "28-cd-c1"
)


def get_ethernet_info():
    """Finds the active Ethernet adapter IP and calculates broadcast address."""
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

    # Calculate broadcast IP
    ip_parts = [int(p) for p in eth_ip.split('.')]
    mask_parts = [int(p) for p in eth_mask.split('.')]
    bcast_parts = [ip_parts[i] | (~mask_parts[i] & 0xFF) for i in range(4)]
    bcast_ip = ".".join(str(p) for p in bcast_parts)

    # Determine offered IP in the same subnet
    offered_parts = list(ip_parts)
    offered_parts[3] = 200 if offered_parts[3] != 200 else 201
    offered_ip = ".".join(str(p) for p in offered_parts)

    return eth_ip, eth_mask, bcast_ip, offered_ip


def ip2bytes(ip_str):
    return socket.inet_aton(ip_str)


def build_dhcp_reply(msg_type, client_xid, client_mac_raw, server_ip, offered_ip, subnet_mask):
    """Constructs standard DHCP Reply (DHCPOFFER or DHCPACK)."""
    packet = bytearray([2, 1, 6, 0])          # Boot reply, Ethernet, 6 bytes hw len, 0 hops
    packet.extend(client_xid)                  # Transaction ID
    packet.extend(b'\x00\x00')                 # Secs
    packet.extend(b'\x80\x00')                 # Flags: Broadcast flag set
    packet.extend(b'\x00\x00\x00\x00')         # ciaddr (client IP)
    packet.extend(ip2bytes(offered_ip))        # yiaddr (your IP)
    packet.extend(ip2bytes(server_ip))         # siaddr (next server IP)
    packet.extend(b'\x00\x00\x00\x00')         # giaddr (relay agent)
    packet.extend(client_mac_raw)              # chaddr (client MAC)
    packet.extend(b'\x00' * 64)                # sname (server host name)
    packet.extend(b'\x00' * 128)               # file (boot file name)
    packet.extend(b'\x63\x82\x53\x63')         # Magic Cookie

    # DHCP Options
    packet.extend(bytes([53, 1, msg_type]))                 # Option 53: DHCP Message Type
    packet.extend(bytes([54, 4]) + ip2bytes(server_ip))      # Option 54: Server Identifier
    packet.extend(bytes([51, 4]) + struct.pack('>I', 86400)) # Option 51: Lease Time (24h)
    packet.extend(bytes([1, 4]) + ip2bytes(subnet_mask))     # Option 1: Subnet Mask
    packet.extend(bytes([3, 4]) + ip2bytes(server_ip))       # Option 3: Router / Gateway
    packet.extend(bytes([6, 4]) + ip2bytes("8.8.8.8"))       # Option 6: Domain Name Server
    packet.append(255)                                      # Option 255: End

    if len(packet) < 300:
        packet.extend(b'\x00' * (300 - len(packet)))
    return bytes(packet)


def run_dhcp_server(timeout_sec=None):
    """
    Runs the DHCP server. If timeout_sec is specified, runs up to that time
    or until an IP is successfully assigned to a Raspberry Pi.
    """
    server_ip, subnet_mask, bcast_ip, offered_ip = get_ethernet_info()
    print("=" * 64)
    print("  🚀 MINI DHCP SERVER FOR RASPBERRY PI DIRECT ETHERNET")
    print(f"  Interface Server IP:  {server_ip}")
    print(f"  Subnet Mask:          {subnet_mask}")
    print(f"  Broadcast IP:         {bcast_ip}")
    print(f"  Offering Pi IP:       {offered_ip}")
    print("=" * 64)

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    try:
        s.bind(('0.0.0.0', 67))
    except Exception as e:
        print(f"[!] ไม่สามารถเปิด Port 67 ได้ (อาจมี Service อื่นใช้งานอยู่): {e}")
        s.close()
        return None

    s.settimeout(1.0)
    start_time = time.time()
    assigned_ip = None

    print(f"[*] กำลังรอรับสัญญาณขอ IP (DHCPDISCOVER) จาก Raspberry Pi...")
    print(f"    (หากเสียบสายแลนค้างไว้นานแล้ว ให้ถอดสายแลนแล้วเสียบใหม่ 1 ครั้ง)")

    try:
        while True:
            if timeout_sec and (time.time() - start_time > timeout_sec):
                break

            try:
                data, addr = s.recvfrom(2048)
                if len(data) < 240:
                    continue

                xid = data[4:8]
                chaddr = data[28:44]
                mac_str = ':'.join(f'{b:02x}' for b in chaddr[:6])

                # Check if it's a known Raspberry Pi MAC, or accept all non-PC clients
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
                    print(f"[+] ได้รับ DHCPDISCOVER จากอุปกรณ์ MAC: {mac_str} {'(Raspberry Pi)' if is_pi else ''}")
                    reply = build_dhcp_reply(2, xid, chaddr, server_ip, offered_ip, subnet_mask)
                    # Send to subnet broadcast address to avoid WinError 10065
                    s.sendto(reply, (bcast_ip, 68))
                    print(f"[+] ส่ง DHCPOFFER เสนอหมายเลข IP: {offered_ip} สำเร็จ")

                elif msg_type == 3:  # DHCPREQUEST
                    print(f"[+] ได้รับ DHCPREQUEST จากอุปกรณ์ MAC: {mac_str}")
                    reply = build_dhcp_reply(5, xid, chaddr, server_ip, offered_ip, subnet_mask)
                    s.sendto(reply, (bcast_ip, 68))
                    print(f"[+] ส่ง DHCPACK ยืนยันการแจก IP: {offered_ip} สำเร็จเรียบร้อย!")
                    assigned_ip = offered_ip
                    if is_pi or timeout_sec:
                        break

            except socket.timeout:
                continue
            except Exception as e:
                print(f"[!] Warning ในการสื่อสาร DHCP: {e}")
                break

    finally:
        s.close()

    return assigned_ip


def main():
    assigned = run_dhcp_server(timeout_sec=None)
    if assigned:
        print(f"\n🎉 บอร์ด Raspberry Pi ได้รับ IP เรียบร้อย: {assigned}")


if __name__ == '__main__':
    main()
