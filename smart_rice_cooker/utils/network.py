"""
network.py - Dynamic Network Resolution & Pi Discovery Utility
Resolves the Raspberry Pi IP dynamically across different Wi-Fi environments.
"""

import os
import socket

import time

DEFAULT_PI_IP = "192.168.88.74"
_CACHED_PI_IP = None
_CACHE_TIME = 0.0

def get_pi_ip(fallback: str = DEFAULT_PI_IP, max_age: float = 60.0) -> str:
    """
    Dynamically discovers and resolves Raspberry Pi IP address with 60s memory caching
    so subsequent calls return in 0.0001s instead of 2+ second mDNS latency.
    """
    global _CACHED_PI_IP, _CACHE_TIME
    env_ip = os.getenv("PI_IP")
    if env_ip:
        return env_ip
    
    now = time.time()
    if _CACHED_PI_IP and (now - _CACHE_TIME) < max_age:
        return _CACHED_PI_IP
    
    try:
        resolved = socket.gethostbyname("raspberrypi.local")
        if resolved and not resolved.startswith("127."):
            _CACHED_PI_IP = resolved
            _CACHE_TIME = now
            return resolved
    except Exception:
        pass
    
    _CACHED_PI_IP = fallback
    _CACHE_TIME = now
    return fallback

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
