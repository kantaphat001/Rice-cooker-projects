"""
network.py - Dynamic Network Resolution & Pi Discovery Utility
Resolves the Raspberry Pi IP dynamically across different Wi-Fi and Ethernet environments.
Supports Dual-Mode:
- When running on Raspberry Pi, dynamically returns the Pi's own active IP.
- When running on PC, discovers and verifies the remote Raspberry Pi IP.
"""

import os
import socket
import time
import subprocess
from pathlib import Path
from typing import Optional

DEFAULT_PI_IP = "10.57.215.17"
_CACHED_PI_IP: Optional[str] = None
_CACHE_TIME: float = 0.0

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


def is_running_on_pi() -> bool:
    """Return True if running directly on the Raspberry Pi."""
    try:
        if Path("/home/pi").is_dir():
            return socket.gethostname() == "raspberrypi" or str(ROOT_DIR).startswith("/home/pi")
    except Exception:
        pass
    return False


def is_port_reachable(ip: str, port: int = 22, timeout: float = 0.3) -> bool:
    """Quickly probes if a host port is open and reachable."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        ok = (s.connect_ex((ip, port)) == 0)
        s.close()
        return ok
    except Exception:
        return False


def get_local_ip() -> str:
    """Returns primary IPv4 address of the host machine."""
    # 1. Try route discovery via UDP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    # 2. Linux hostname -I (works offline without internet access)
    try:
        res = subprocess.run(["hostname", "-I"], capture_output=True, text=True, timeout=1)
        for candidate in res.stdout.strip().split():
            if candidate and not candidate.startswith("127."):
                return candidate
    except Exception:
        pass

    # 3. Fallback to gethostbyname
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass

    return "127.0.0.1"


def get_pi_ip(fallback: str = DEFAULT_PI_IP, max_age: float = 30.0) -> str:
    """
    Dynamically discovers and resolves Raspberry Pi IP address.
    Verifies reachability before returning stale IPs.
    """
    global _CACHED_PI_IP, _CACHE_TIME
    env_ip = os.getenv("PI_IP")
    if env_ip:
        return env_ip

    # If running directly on the Raspberry Pi, Pi IP is this host's local IP!
    if is_running_on_pi():
        local_ip = get_local_ip()
        _CACHED_PI_IP = local_ip
        _CACHE_TIME = time.time()
        cfg_file = ROOT_DIR / "config_ip.txt"
        try:
            cfg_file.write_text(local_ip, encoding="utf-8")
        except Exception:
            pass
        return local_ip

    now = time.time()
    if _CACHED_PI_IP and (now - _CACHE_TIME) < max_age:
        if is_port_reachable(_CACHED_PI_IP, 22, 0.2) or is_port_reachable(_CACHED_PI_IP, 8080, 0.2):
            return _CACHED_PI_IP

    cfg_file = ROOT_DIR / "config_ip.txt"
    saved_ip = None
    if cfg_file.exists():
        try:
            val = cfg_file.read_text(encoding="utf-8").strip()
            if val:
                saved_ip = val
        except Exception:
            pass

    # Priority 1: Check saved IP if reachable
    if saved_ip:
        if is_port_reachable(saved_ip, 22, 0.25) or is_port_reachable(saved_ip, 8080, 0.25):
            _CACHED_PI_IP = saved_ip
            _CACHE_TIME = now
            return saved_ip

    # Priority 2: Check mDNS raspberrypi.local
    try:
        resolved = socket.gethostbyname("raspberrypi.local")
        if resolved and not resolved.startswith("127."):
            if is_port_reachable(resolved, 22, 0.25) or is_port_reachable(resolved, 8080, 0.25):
                _CACHED_PI_IP = resolved
                _CACHE_TIME = now
                try:
                    cfg_file.write_text(resolved, encoding="utf-8")
                except Exception:
                    pass
                return resolved
    except Exception:
        pass

    # Priority 3: Probe known active candidates
    for candidate in [fallback, "10.57.215.17", "192.168.137.102"]:
        if is_port_reachable(candidate, 22, 0.2) or is_port_reachable(candidate, 8080, 0.2):
            _CACHED_PI_IP = candidate
            _CACHE_TIME = now
            try:
                cfg_file.write_text(candidate, encoding="utf-8")
            except Exception:
                pass
            return candidate

    cand = saved_ip or fallback
    _CACHED_PI_IP = cand
    _CACHE_TIME = now
    return cand
