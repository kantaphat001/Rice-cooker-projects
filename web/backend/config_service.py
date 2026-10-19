"""
Configuration service for Smart Rice Cooker Web Manager.
Handles loading, saving, and background synchronization of med_config.json to Raspberry Pi.
"""
import json
import threading
from pathlib import Path
from typing import Dict, Any

from web.backend.network_utils import get_pi_ip

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT_DIR / "med_config.json"
EXAMPLE_CONFIG_PATH = ROOT_DIR / "med_config.example.json"

PI_USER = "pi"
PI_PASS = "1234"

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


def load_config() -> Dict[str, Any]:
    """Load medication and member configuration safely."""
    if CONFIG_PATH.is_file():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Error reading config: {e}")

    # Fallback to example configuration if active config does not exist
    if EXAMPLE_CONFIG_PATH.is_file():
        try:
            with open(EXAMPLE_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    return {"members": {}}


def save_config(config_data: Dict[str, Any]) -> bool:
    """Save configuration to disk and trigger background sync to Raspberry Pi."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        # Trigger background SFTP sync
        threading.Thread(target=_sync_config_to_pi, daemon=True).start()
        return True
    except Exception as e:
        print(f"[!] Error saving config: {e}")
        return False


def _sync_config_to_pi() -> None:
    """Synchronize med_config.json to Raspberry Pi in the background."""
    if not PARAMIKO_AVAILABLE:
        return
    pi_ip = get_pi_ip()
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(pi_ip, username=PI_USER, password=PI_PASS, timeout=5)
        sftp = ssh.open_sftp()
        sftp.put(str(CONFIG_PATH), f"/home/{PI_USER}/med_config.json")
        sftp.close()
        ssh.close()
        print(f"[+] Synced med_config.json to Raspberry Pi ({pi_ip})")
    except Exception as e:
        print(f"[!] Failed to sync config to Pi ({pi_ip}): {e}")
