"""
Network utilities for Smart Rice Cooker Web Manager.
Provides LAN IP auto-detection and cached Raspberry Pi discovery.
"""
import socket
import time
from pathlib import Path
from typing import Optional

_CACHED_PI_IP: Optional[str] = None
_CACHED_PI_TIME: float = 0.0
_CACHE_TTL: float = 60.0  # Cache Pi IP for 60 seconds to guarantee <0.1ms responses


def get_local_ip() -> str:
    """Return the LAN IP address of this computer."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def get_pi_ip(timeout: float = 0.3) -> str:
    """
    Discover Raspberry Pi IP on the local network.
    Checks config_ip.txt first, then memory cache, then attempts mDNS (raspberrypi.local).
    Caches results aggressively to prevent UI latency.
    """
    global _CACHED_PI_IP, _CACHED_PI_TIME

    # Check config_ip.txt
    cfg_file = Path(__file__).resolve().parent.parent.parent / "config_ip.txt"
    if cfg_file.exists():
        try:
            saved_ip = cfg_file.read_text(encoding="utf-8").strip()
            if saved_ip:
                return saved_ip
        except Exception:
            pass

    now = time.time()
    if _CACHED_PI_IP and (now - _CACHED_PI_TIME < _CACHE_TTL):
        return _CACHED_PI_IP

    # 1. Try resolving mDNS hostname
    try:
        ip = socket.gethostbyname('raspberrypi.local')
        if ip and not ip.startswith('127.'):
            _CACHED_PI_IP = ip
            _CACHED_PI_TIME = now
            return ip
    except Exception:
        pass

    # 2. Known default static / previous IP fallback
    fallback_ip = '192.168.88.74'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(min(timeout, 0.3))
        if s.connect_ex((fallback_ip, 22)) == 0:
            s.close()
            _CACHED_PI_IP = fallback_ip
            _CACHED_PI_TIME = now
            return fallback_ip
        s.close()
    except Exception:
        pass

    # Cache fallback result so subsequent calls take <0.0001s
    _CACHED_PI_IP = fallback_ip
    _CACHED_PI_TIME = now
    return fallback_ip
