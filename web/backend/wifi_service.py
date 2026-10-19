"""
Wi-Fi provisioning service for Raspberry Pi.
Manages network status, scanning, and saving remote Wi-Fi networks via deploy.wifi_manager.
"""
from typing import Dict, Any, List, Tuple
from deploy.wifi_manager import (
    get_current_wifi,
    scan_available_wifi,
    list_saved_wifi,
    add_wifi_network
)
from web.backend.network_utils import get_pi_ip


def get_wifi_status() -> Dict[str, Any]:
    """Return current connection, saved connections, and Pi IP."""
    current = get_current_wifi()
    saved = list_saved_wifi()
    return {
        "current": current,
        "saved": saved,
        "pi_ip": get_pi_ip()
    }


def scan_wifi() -> List[Dict[str, Any]]:
    """Scan and return nearby Wi-Fi networks."""
    return scan_available_wifi()


def add_wifi(ssid: str, password: str) -> Tuple[bool, str]:
    """Add a new Wi-Fi profile to Raspberry Pi."""
    return add_wifi_network(ssid, password)
