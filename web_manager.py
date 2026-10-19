"""
web_manager.py - Smart Rice Cooker Web Management Portal Entrypoint
Zero-dependency, multi-threaded companion server with Apple Minimalist UI (2026 Edition).
Seamlessly connects with Raspberry Pi via mDNS and SFTP.
"""
import sys
from pathlib import Path

# Ensure project root is in Python module path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web.backend.server import run_server

if __name__ == '__main__':
    run_server()
