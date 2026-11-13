"""
shutdown_pi.py - 1-Click Safe Shutdown for Raspberry Pi Companion Box
Flushes disk caches, turns off camera, turns off LEDs, stops cooling fan relay,
stops services, and shuts down safely.
"""

import sys
import io
from pathlib import Path

# UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web.backend.system_service import safe_shutdown_pi

def shutdown_pi(reboot: bool = False) -> bool:
    action_name = "รีบูตเครื่อง (Reboot)" if reboot else "ปิดเครื่องอย่างปลอดภัย (Safe Shutdown)"
    print("=" * 65)
    print(f"   🛑 RASPBERRY PI 1-CLICK POWER MANAGER: {action_name}")
    print("=" * 65)

    ok, msg = safe_shutdown_pi(reboot=reboot)
    if ok:
        print(f"\n[✅] {msg}")
    else:
        print(f"\n[!] {msg}")
        print("    กรุณาตรวจสอบว่าบอร์ดเปิดอยู่ หรือเสียบสาย LAN / ต่อ Wi-Fi เดียวกันครับ")
    print("=" * 65)
    return ok

if __name__ == "__main__":
    is_reboot = "--reboot" in sys.argv
    success = shutdown_pi(reboot=is_reboot)
    if not ("--no-pause" in sys.argv):
        input("\nกด Enter เพื่อปิดหน้าต่างนี้...")
