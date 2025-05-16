import cv2
from ultralytics import YOLO
from db import log_violation
import time

# Load your trained model
model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train16\weights\best.pt')

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
                    log_violation(label, confidence)
                    last_logged[label] = now

        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()
