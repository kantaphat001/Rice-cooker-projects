"""
network.py - Dynamic Network Resolution & Pi Discovery Utility
Resolves the Raspberry Pi IP dynamically across different Wi-Fi and Ethernet environments.
"""

import os
import socket
import time
import subprocess
from pathlib import Path

DEFAULT_PI_IP = "192.168.88.74"
_CACHED_PI_IP = None
_CACHE_TIME = 0.0


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


def get_pi_ip(fallback: str = DEFAULT_PI_IP, max_age: float = 30.0) -> str:
    """
    Dynamically discovers and resolves Raspberry Pi IP address.
    Verifies reachability before returning stale IPs.
    """
    global _CACHED_PI_IP, _CACHE_TIME
    env_ip = os.getenv("PI_IP")
    if env_ip:
        return env_ip

    now = time.time()
    if _CACHED_PI_IP and (now - _CACHE_TIME) < max_age:
        if is_port_reachable(_CACHED_PI_IP, 22, 0.2) or is_port_reachable(_CACHED_PI_IP, 3389, 0.2):
            return _CACHED_PI_IP

    cfg_file = Path(__file__).resolve().parent.parent.parent / "config_ip.txt"
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
        if is_port_reachable(saved_ip, 22, 0.3) or is_port_reachable(saved_ip, 3389, 0.3):
            _CACHED_PI_IP = saved_ip
            _CACHE_TIME = now
            return saved_ip

    # Priority 2: Check mDNS raspberrypi.local
    try:
        resolved = socket.gethostbyname("raspberrypi.local")
        if resolved and not resolved.startswith("127."):
            if is_port_reachable(resolved, 22, 0.3) or is_port_reachable(resolved, 3389, 0.3):
                _CACHED_PI_IP = resolved
                _CACHE_TIME = now
                try:
                    cfg_file.write_text(resolved, encoding="utf-8")
                except Exception:
                    pass
                return resolved
    except Exception:
        pass

    # Priority 3: Fallback to saved_ip or DEFAULT_PI_IP
    cand = saved_ip or fallback
    _CACHED_PI_IP = cand
    _CACHE_TIME = now
    return cand


def get_local_ip() -> str:
    """Returns primary IPv4 address of the host machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
