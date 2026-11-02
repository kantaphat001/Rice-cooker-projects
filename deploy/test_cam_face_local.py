import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.50.49.17', username='pi', password='1234', timeout=5)

script = """
import cv2
import time
from smart_rice_cooker.vision.yunet_detector import YuNetDetector
from smart_rice_cooker.config import settings

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1)

ret, frame = cap.read()
cap.release()

if ret and frame is not None:
    print(f"Captured frame: shape={frame.shape}")
    detector = YuNetDetector(settings.YUNET_MODEL_FILE)
    faces = detector.detect(frame)
    print(f"Faces detected: {len(faces) if faces is not None else 0}")
    if faces is not None and len(faces) > 0:
        box = faces[0][:4]
        print(f"Face box: {box}")
else:
    print("Failed to capture frame from camera")
"""

sftp = ssh.open_sftp()
with sftp.open('/tmp/test_cam_face.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('PYTHONPATH=/home/pi python3 /tmp/test_cam_face.py')
print(stdout.read().decode())
print(stderr.read().decode())
ssh.close()
