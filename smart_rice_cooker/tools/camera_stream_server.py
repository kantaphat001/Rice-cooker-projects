"""
camera_stream_server.py - Live Web Camera Stream with YuNet Face Detection
Streams camera frames over HTTP (port 8080) so users can view live video from any browser.
"""

import cv2
import time
import os
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("cam_stream")

# Path to YuNet model
MODEL_PATH = "/home/pi/smart_rice_cooker/models/face_detection_yunet_2023mar.onnx"
detector = None
if os.path.exists(MODEL_PATH):
    try:
        detector = cv2.FaceDetectorYN.create(MODEL_PATH, "", (640, 480), 0.5, 0.3, 5000)
        logger.info("[StreamServer] YuNet Face Detector loaded successfully.")
    except Exception as e:
        logger.warning(f"[StreamServer] Could not load YuNet: {e}")

class CameraStreamer:
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open camera index {camera_index}")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.lock = threading.Lock()
        self.running = True
        self.latest_jpeg = None
        self.face_count = 0
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _update_loop(self):
        fps_time = time.time()
        fps = 0
        frame_count = 0

        while self.running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                time.sleep(0.03)
                continue

            frame_count += 1
            if time.time() - fps_time >= 1.0:
                fps = frame_count / (time.time() - fps_time)
                frame_count = 0
                fps_time = time.time()

            # Run YuNet face detection if available
            faces_found = 0
            if detector is not None:
                detector.setInputSize((frame.shape[1], frame.shape[0]))
                _, faces = detector.detect(frame)
                if faces is not None:
                    faces_found = len(faces)
                    for face in faces:
                        box = [int(v) for v in face[:4]]
                        conf = face[-1]
                        x, y, w, h = box
                        # Draw bounding box
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        label = f"Face: {conf*100:.1f}%"
                        cv2.putText(frame, label, (x, max(20, y - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                        # Landmarks
                        for i in range(5):
                            lx = int(face[4 + i * 2])
                            ly = int(face[5 + i * 2])
                            cv2.circle(frame, (lx, ly), 3, (255, 0, 0), -1)

            self.face_count = faces_found

            # Draw HUD
            hud = f"Smart Rice Cooker Cam | 640x480 @ {fps:.1f} FPS | Faces: {faces_found}"
            cv2.rectangle(frame, (0, 0), (640, 28), (20, 20, 20), -1)
            cv2.putText(frame, hud, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

            ret_enc, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
            if ret_enc:
                with self.lock:
                    self.latest_jpeg = jpeg.tobytes()

            time.sleep(0.01)

    def get_frame(self):
        with self.lock:
            return self.latest_jpeg

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()

streamer = None

class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Rice Cooker - Live Camera Stream</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: white; margin: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 100vh; }
        .card { background: #1e293b; border-radius: 16px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); text-align: center; max-width: 680px; width: 95%; }
        h1 { margin-top: 0; font-size: 22px; color: #38bdf8; display: flex; align-items: center; justify-content: center; gap: 8px; }
        .stream-box { border-radius: 12px; overflow: hidden; border: 3px solid #334155; margin: 16px 0; background: #000; line-height: 0; }
        img { width: 100%; height: auto; display: block; }
        .status { display: flex; justify-content: space-around; background: #0f172a; padding: 12px; border-radius: 8px; font-size: 14px; color: #94a3b8; }
        .status b { color: #4ade80; }
        .pulse { display: inline-block; width: 10px; height: 10px; border-radius: 50%; background: #22c55e; margin-right: 6px; box-shadow: 0 0 8px #22c55e; }
    </style>
</head>
<body>
    <div class="card">
        <h1><span class="pulse"></span>กล้องหม้อหุงข้าวอัจฉริยะ (Live View)</h1>
        <div class="stream-box">
            <img src="/stream.mjpg" alt="Live Camera Stream">
        </div>
        <div class="status">
            <div>ความละเอียด: <b>640x480 (MJPG)</b></div>
            <div>AI ตรวจจับใบหน้า: <b>YuNet ONNX</b></div>
            <div>สถานะกล้อง: <b>ONLINE 🟢</b></div>
        </div>
    </div>
</body>
</html>
            """
            self.wfile.write(html.encode("utf-8"))

        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", "0")
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=FRAME")
            self.end_headers()

            try:
                while True:
                    frame = streamer.get_frame() if streamer else None
                    if frame is not None:
                        self.wfile.write(b"--FRAME\r\n")
                        self.send_header("Content-Type", "image/jpeg")
                        self.send_header("Content-Length", str(len(frame)))
                        self.end_headers()
                        self.wfile.write(frame)
                        self.wfile.write(b"\r\n")
                    time.sleep(0.03)
            except (BrokenPipeError, ConnectionResetError):
                pass
        else:
            self.send_error(404)

def run(port=8080):
    global streamer
    logger.info("[StreamServer] Initializing Camera...")
    streamer = CameraStreamer(camera_index=0)
    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, StreamHandler)
    logger.info(f"[StreamServer] 🌐 Server running at http://0.0.0.0:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("[StreamServer] Shutting down...")
        if streamer:
            streamer.stop()
        httpd.server_close()

if __name__ == "__main__":
    run()
