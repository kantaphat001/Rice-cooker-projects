"""
pi_camera_window.py - Live Camera Preview Window on Raspberry Pi Desktop
Automatically detects active X11 display (:10 for XRDP or :0 for HDMI),
temporarily releases camera from background service, and renders real-time
video feed with YuNet neural face detection overlays directly on the Pi screen.
"""

import cv2
import time
import os
import sys
import subprocess
from pathlib import Path

# Auto-detect active X11 display
def get_display():
    if os.getenv("DISPLAY"):
        return os.getenv("DISPLAY")
    for disp in [":10", ":0"]:
        sock = f"/tmp/.X11-unix/X{disp.replace(':', '')}"
        if os.path.exists(sock):
            return disp
    return ":0"

os.environ["DISPLAY"] = get_display()
print(f"[*] Target Display: {os.environ['DISPLAY']}")

# Check if smart-cooker.service is running and stop it to free /dev/video0
service_was_running = False
try:
    check = subprocess.run(["systemctl", "is-active", "smart-cooker.service"],
                           capture_output=True, text=True)
    if "active" in check.stdout.strip():
        print("[*] Pausing background smart-cooker service to access camera...")
        subprocess.run(["sudo", "systemctl", "stop", "smart-cooker.service"])
        service_was_running = True
        time.sleep(1.0)
except Exception:
    pass

# Load YuNet Model
MODEL_PATH = "/home/pi/smart_rice_cooker/models/face_detection_yunet_2023mar.onnx"
detector = None
if os.path.exists(MODEL_PATH):
    try:
        detector = cv2.FaceDetectorYN.create(MODEL_PATH, "", (640, 480), 0.5, 0.3, 5000)
        print("[+] YuNet Face Detector loaded.")
    except Exception as e:
        print(f"[!] Warning: YuNet init error: {e}")

# Open Camera
print("[*] Initializing camera /dev/video0...")
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[-] Error: Cannot open camera /dev/video0")
    if service_was_running:
        subprocess.run(["sudo", "systemctl", "start", "smart-cooker.service"])
    sys.exit(1)

cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

window_name = "Smart Rice Cooker - Camera & Face AI Preview"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.resizeWindow(window_name, 640, 480)

print("=" * 70)
print(f" [+] Camera window successfully opened on Display {os.environ['DISPLAY']}!")
print("     - Look at your Raspberry Pi screen (Remote Desktop / XRDP)!")
print("     - Press 'q' or 'ESC' to close the window.")
print("=" * 70)

fps_time = time.time()
fps = 0
frame_count = 0

try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue

        frame_count += 1
        if time.time() - fps_time >= 1.0:
            fps = frame_count / (time.time() - fps_time)
            frame_count = 0
            fps_time = time.time()

        # YuNet Face Detection
        num_faces = 0
        if detector is not None:
            detector.setInputSize((frame.shape[1], frame.shape[0]))
            _, faces = detector.detect(frame)
            if faces is not None:
                num_faces = len(faces)
                for face in faces:
                    x, y, w, h = [int(v) for v in face[:4]]
                    conf = face[-1]
                    # Draw green bounding box
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(frame, f"Face: {conf*100:.1f}%", (x, max(25, y - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    # 5 facial landmarks
                    for i in range(5):
                        lx = int(face[4 + i * 2])
                        ly = int(face[5 + i * 2])
                        cv2.circle(frame, (lx, ly), 3, (255, 100, 0), -1)

        # Status overlay
        cv2.rectangle(frame, (0, 0), (640, 32), (30, 30, 30), -1)
        cv2.putText(frame, f"Pi Camera Live | {fps:.1f} FPS | Faces: {num_faces} | Press 'q' to exit",
                    (12, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        cv2.imshow(window_name, frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:  # 'q' or ESC
            break

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("[+] Camera window closed.")
    if service_was_running:
        print("[*] Resuming background smart-cooker service...")
        subprocess.run(["sudo", "systemctl", "start", "smart-cooker.service"])
        print("[+] Background service resumed.")

if __name__ == "__main__":
    pass
