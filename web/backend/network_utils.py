"""
network_utils.py - Network utilities for Smart Rice Cooker Web Manager.
Provides LAN IP auto-detection and cached Raspberry Pi discovery.
Supports Dual-Mode:
- When running directly on Raspberry Pi, local IP is automatically detected as the Pi IP.
- When running on PC, discovers and verifies the remote Raspberry Pi IP.
"""
import socket
import time
import subprocess
from pathlib import Path
from typing import Optional

_CACHED_PI_IP: Optional[str] = None
_CACHED_PI_TIME: float = 0.0
_CACHE_TTL: float = 30.0

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def is_running_on_pi() -> bool:
    """Return True if running directly on the Raspberry Pi."""
    try:
        if Path("/home/pi").is_dir():
            # Check if current executing root is on /home/pi
            return str(ROOT_DIR).startswith("/home/pi") or socket.gethostname() == "raspberrypi"
    except Exception:
        pass
    return False


def get_local_ip() -> str:
    """Return the LAN IP address of this computer or Raspberry Pi."""
    # 1. Try UDP connection to well-known address (does not send packets, grabs route)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    # 2. On Linux/Pi: try hostname -I (works even when totally offline without internet)
    try:
        res = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=1)
        ips = res.stdout.strip().split()
        for ip in ips:
            if ip and not ip.startswith('127.'):
                return ip
    except Exception:
        pass

    # 3. Fallback to socket gethostbyname
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith('127.'):
            return ip
    except Exception:
        pass

    return '127.0.0.1'


def is_port_open(ip: str, port: int = 22, timeout: float = 0.3) -> bool:
    """Quickly probe if a port is open."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        ok = (s.connect_ex((ip, port)) == 0)
        s.close()
        return ok
    except Exception:
        return False


def get_pi_ip(timeout: float = 0.3) -> str:
    """
    Discover Raspberry Pi IP on the local network.
    - If running on Pi, returns this Pi's current active LAN IP.
    - If running on PC, checks config_ip.txt, cache, and mDNS.
    """
    global _CACHED_PI_IP, _CACHED_PI_TIME

    # 1. If running natively on the Raspberry Pi, the Pi IP is the local LAN IP!
    if is_running_on_pi():
        local_ip = get_local_ip()
        _CACHED_PI_IP = local_ip
        _CACHED_PI_TIME = time.time()
        # Save to config_ip.txt for local consistency
        cfg_file = ROOT_DIR / "config_ip.txt"
        try:
            cfg_file.write_text(local_ip, encoding="utf-8")
        except Exception:
            pass
        return local_ip

    now = time.time()
    cfg_file = ROOT_DIR / "config_ip.txt"

    # 2. Check config_ip.txt (supports multiple lines: active IP first, previous IPs as backups)
    saved_candidates = []
    if cfg_file.exists():
        try:
            raw_text = cfg_file.read_text(encoding="utf-8")
            saved_candidates = [line.strip() for line in raw_text.replace(",", "\n").splitlines() if line.strip() and not line.strip().startswith("#")]
            for saved_ip in saved_candidates:
                if is_port_open(saved_ip, 22, timeout=0.25) or is_port_open(saved_ip, 8080, timeout=0.25):
                    _CACHED_PI_IP = saved_ip
                    _CACHED_PI_TIME = now
                    return saved_ip
        except Exception:
            pass

    if _CACHED_PI_IP and (now - _CACHED_PI_TIME < _CACHE_TTL):
        return _CACHED_PI_IP

    # 3. Try resolving mDNS hostname (raspberrypi.local)
    try:
        ip = socket.gethostbyname('raspberrypi.local')
        if ip and not ip.startswith('127.'):
            if is_port_open(ip, 22, timeout=0.2) or is_port_open(ip, 8080, timeout=0.2):
                _CACHED_PI_IP = ip
                _CACHED_PI_TIME = now
                try:
                    cfg_file.write_text(ip, encoding="utf-8")
                except Exception:
                    pass
                return ip
    except Exception:
        pass

    # 4. Check ARP table for Raspberry Pi MAC addresses or active devices
    try:
        res = subprocess.run(['arp', '-a'], capture_output=True, text=True, timeout=1)
        for line in res.stdout.splitlines():
            line_clean = line.strip().lower()
            if any(mac_prefix in line_clean for mac_prefix in ("d8-3a-dd", "d8:3a:dd", "b8-27-eb", "b8:27:eb", "dc-a6-32", "dc:a6:32", "e4-5f-01", "e4:5f:01", "28-cd-c1", "28:cd:c1")):
                import re
                m = re.search(r'(\d{1,3}(?:\.\d{1,3}){3})', line)
                if m:
                    cand_arp = m.group(1)
                    if is_port_open(cand_arp, 22, timeout=0.25) or is_port_open(cand_arp, 8080, timeout=0.25):
                        _CACHED_PI_IP = cand_arp
                        _CACHED_PI_TIME = now
                        return cand_arp
    except Exception:
        pass

    # 5. Known recent IP list (all previous Hotspots & LAN subnets)
    known_ips = ['10.68.140.13', '10.57.215.17', '192.168.137.102', '192.168.88.74', '172.20.3.37']
    for candidate in known_ips:
        if is_port_open(candidate, 22, timeout=0.2) or is_port_open(candidate, 8080, timeout=0.2):
            _CACHED_PI_IP = candidate
            _CACHED_PI_TIME = now
            return candidate

    first_saved = saved_candidates[0] if saved_candidates else '10.57.215.17'
    return _CACHED_PI_IP or first_saved
