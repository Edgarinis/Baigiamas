import cv2
from ultralytics import YOLO
from db import log_violation
import time
import datetime
import os

# Load your trained model
model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train17\weights\best.pt')

SNAPSHOT_DIR = os.path.join('static', 'snapshots')
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

VIOLATION_CLASSES = ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']
last_logged = {}
COOLDOWN_SECONDS = 3


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success:
            break

        results = model(frame, conf=0.3)
        annotated_frame = results[0].plot()

        for box in results[0].boxes.data.tolist():
            class_id = int(box[5])
            confidence = box[4]
            label = model.names[class_id]

            if label in VIOLATION_CLASSES and confidence > 0.4:
                now = time.time()
                last_time = last_logged.get(label, 0)
                if now - last_time > COOLDOWN_SECONDS:
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = f"{label.replace(' ', '_')}_{timestamp}.jpg"
                    snapshot_path = os.path.join(SNAPSHOT_DIR, filename)
                    cv2.imwrite(snapshot_path, frame)

                    relative_path = os.path.relpath(snapshot_path, start='static').replace('\\', '/')
                    log_violation(label, confidence, relative_path)
                    last_logged[label] = now

        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
