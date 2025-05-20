import cv2, time, datetime, os, requests, config
from ultralytics import YOLO
from src.db import log_violation
from flask import current_app
import numpy as np

model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train17\weights\best.pt')

SNAPSHOT_DIR = os.path.join('static', 'snapshots')
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

last_logged = {}
COOLDOWN_SECONDS = 3

def fetch_active_classes():
    try:
        resp = requests.get('http://127.0.0.1:5000/get_active_classes')
        if resp.status_code == 200:
            return set(resp.json())
    except:
        pass
    return {'NO-Hardhat','NO-Mask','NO-Safety Vest'}

def generate_frames():
    cap = None
    active_classes = fetch_active_classes()
    last_check = time.time()

    while True:
        # 1) If STREAM_ACTIVE is False, pause here
        if not config.STREAM_ACTIVE:
            if cap is not None:
                cap.release()
                cap = None
            time.sleep(0.1)
            continue

        # 2) Lazy-open the camera only once streaming turns on
        if cap is None:
            source = config.VIDEO_SOURCE
            cap = cv2.VideoCapture(source, cv2.CAP_ANY)
        success, frame = cap.read()
        if not success:
            break

        # 3) Refresh active_classes every 5 seconds
        if time.time() - last_check > 5:
            active_classes = fetch_active_classes()
            last_check = time.time()

        # 4) Run YOLO inference
        results = model(frame, conf=0.3)

        # 5) Filter boxes and log snapshots with cooldown
        new_boxes = []
        for box in results[0].boxes.data.tolist():
            cls_id, conf = int(box[5]), box[4]
            label = results[0].names[cls_id]
            if label not in active_classes:
                continue
            new_boxes.append(box)

            now = time.time()
            if now - last_logged.get(label, 0) > COOLDOWN_SECONDS:
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                fname = f"{label.replace(' ','_')}_{ts}.jpg"
                path = os.path.join(SNAPSHOT_DIR, fname)
                cv2.imwrite(path, frame)
                rel = os.path.relpath(path, 'static').replace('\\','/')
                log_violation(label, float(conf), rel)
                last_logged[label] = now

        # 6) Replace the model's boxes with our filtered list
        results[0].boxes.data = np.array(new_boxes)
        annotated = results[0].plot()

        # 7) Encode and yield as MJPEG frame
        _, buf = cv2.imencode('.jpg', annotated)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buf.tobytes() + b'\r\n')

    # Clean up
    if cap:
        cap.release()
