"""
network.py - Dynamic Network Resolution & Pi Discovery Utility
Resolves the Raspberry Pi IP dynamically across different Wi-Fi environments.
"""

import os
import socket

DEFAULT_PI_IP = "192.168.88.74"

def get_pi_ip(fallback: str = DEFAULT_PI_IP) -> str:
    """
    Dynamically discovers and resolves Raspberry Pi IP address:
    1. Checks environment variable PI_IP (if specified).
    2. Resolves mDNS hostname 'raspberrypi.local'.
    3. Falls back to default known IP if mDNS is not responsive.
    """
    env_ip = os.getenv("PI_IP")
    if env_ip:
        return env_ip
    
    try:
        resolved = socket.gethostbyname("raspberrypi.local")
        if resolved and not resolved.startswith("127."):
            return resolved
    except Exception:
        pass
    
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
