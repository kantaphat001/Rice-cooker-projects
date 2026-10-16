"""
main.py - Entrypoint for Smart Rice Cooker Companion Box
Usage:
    python3 -m smart_rice_cooker.main [--gui] [--headless] [--rebuild-faces]
"""

import sys
import os
import argparse
import logging
import signal

from .config import settings
from .service import CompanionService
from .ui.native_gui import NativeElderlyGUI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smart_cooker")

def main():
    parser = argparse.ArgumentParser(description="Smart Rice Cooker Companion Box")
    parser.add_argument("--gui", action="store_true", help="Launch native Tkinter GUI")
    parser.add_argument("--headless", action="store_true", help="Run without graphical display")
    parser.add_argument("--camera-only", action="store_true", help="Run in camera-only mode (bypasses ultrasonic sensor, uses camera face presence)")
    parser.add_argument("--rebuild-faces", action="store_true", help="Rebuild face recognition embeddings database")
    args = parser.parse_args()

    gui_instance = None
    if args.gui or (not args.headless and os.getenv("DISPLAY")):
        gui_instance = NativeElderlyGUI(fullscreen=False)

    service = CompanionService(gui=gui_instance, camera_only=args.camera_only)

    if gui_instance:
        gui_instance.on_ack_callback = service._handle_button_press

    if args.rebuild_faces:
        logger.info("Rebuilding face embeddings...")
        service.face_db.rebuild_database()
        logger.info("Face database rebuilt. Exiting.")
        return

    def sigint_handler(sig, frame):
        logger.info("Interrupt received, stopping service...")
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    service.start()

    if gui_instance and not gui_instance._is_headless:
        # Tkinter mainloop takes over the main thread
        gui_instance.start()
    else:
        # Headless keep-alive loop
        logger.info("Running in headless console mode. Press Ctrl+C to exit.")
        try:
            while True:
                signal.pause() if hasattr(signal, "pause") else sys.stdin.read()
        except (KeyboardInterrupt, SystemExit):
            service.stop()

if __name__ == "__main__":
    main()
