from flask import Flask, render_template, Response
from ultralytics import YOLO
import cv2

app = Flask(__name__)

# Load trained model
model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train9\weights\best.pt')

# Webcam video generator
def generate_frames():
    cap = cv2.VideoCapture(0)  # Webcam
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Run YOLOv8 inference
        results = model(frame, conf =0.5)
        annotated_frame = results[0].plot()

        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
