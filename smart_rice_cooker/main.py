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

    # Fast, isolated rebuild without claiming hardware pins or camera devices
    if args.rebuild_faces:
        logger.info("Rebuilding face embeddings...")
        from .vision.yunet_detector import YuNetDetector
        from .vision.sface_recognizer import SFaceRecognizer
        from .vision.face_database import FaceDatabase
        detector = YuNetDetector(settings.YUNET_MODEL_FILE, conf_threshold=settings.FACE_DETECTION_CONFIDENCE)
        recognizer = SFaceRecognizer(settings.SFACE_MODEL_FILE)
        face_db = FaceDatabase(
            dataset_dir=settings.DATASET_DIR,
            detector=detector,
            recognizer=recognizer,
            match_threshold=settings.FACE_RECOGNITION_THRESHOLD
        )
        face_db.rebuild_database()
        logger.info("Face database rebuilt successfully. Exiting.")
        return

    from .service import CompanionService
    from .ui.native_gui import NativeElderlyGUI

    gui_instance = None
    if args.gui or (not args.headless and os.getenv("DISPLAY")):
        gui_instance = NativeElderlyGUI(fullscreen=False)

    service = CompanionService(gui=gui_instance, camera_only=args.camera_only)

    if gui_instance:
        gui_instance.on_ack_callback = service._handle_button_press

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
        while service._running:
            import time
            time.sleep(1.0)

if __name__ == "__main__":
    main()
