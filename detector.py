import cv2
from ultralytics import YOLO
from db import log_violation
import time
import datetime
import os
import requests
import numpy as np

model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train17\weights\best.pt')

SNAPSHOT_DIR = os.path.join('static', 'snapshots')
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

last_logged = {}
COOLDOWN_SECONDS = 3

# Helper function to get active class list from Flask API
def fetch_active_classes():
    try:
        response = requests.get('http://127.0.0.1:5000/get_active_classes')
        if response.status_code == 200:
            return set(response.json())
    except Exception:
        pass
    return set(['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest'])  # fallback


def generate_frames():
    cap = cv2.VideoCapture(0)
    active_classes = fetch_active_classes()
    last_check = time.time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        if time.time() - last_check > 5:
            active_classes = fetch_active_classes()
            last_check = time.time()

        results = model(frame, conf=0.3)

        # Prepare new detection results with only active classes
        new_boxes = []
        for box in results[0].boxes.data.tolist():
            class_id = int(box[5])
            confidence = box[4]
            label = model.names[class_id]

            if label in active_classes:
                new_boxes.append(box)

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

        # Replace original boxes with filtered list
        results[0].boxes.data = np.array(new_boxes)
        annotated_frame = results[0].plot()

        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
