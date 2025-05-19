from flask import render_template, Response, request, redirect, url_for, jsonify, current_app
from detector import generate_frames
from db import get_violations, log_violation, get_violations_summary, get_class_distribution, get_latest_violation
from ultralytics import YOLO
import os
import datetime
import json

model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train17\weights\best.pt')

VIOLATION_CLASSES = ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']
active_violation_filters = set(VIOLATION_CLASSES)


def configure_routes(app):
    @app.route('/')
    def index():
        total_violations, top_label, top_count = get_violations_summary()
        class_dist = get_class_distribution()
        recent = get_latest_violation()

        return render_template('index.html',
            total_violations=total_violations,
            top_violation_label=top_label,
            top_violation_count=top_count,
            class_distribution=class_dist,
            recent_snapshot=recent
        )

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/violations')
    def violations():
        rows = get_violations()
        return render_template('violations.html', rows=rows)

    @app.route('/detect_image', methods=['POST'])
    def detect_image():
        if 'image' not in request.files:
            return redirect(url_for('index'))

        file = request.files['image']
        if file.filename == '':
            return redirect(url_for('index'))

        # Save upload and run detection
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"img_{timestamp}.jpg"
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        result_path = os.path.join(current_app.config['RESULT_FOLDER'], filename)
        file.save(upload_path)

        results = model(upload_path, conf=0.3)
        results[0].save(filename=result_path)

        # Log first violation if found
        labels = results[0].names
        boxes = results[0].boxes.data.tolist()
        found = None
        for box in boxes:
            class_id = int(box[5])
            confidence = box[4]
            label = labels[class_id]
            if label in VIOLATION_CLASSES:
                found = (label, confidence)
                break
        if found:
            rel_path = os.path.relpath(result_path, start='static').replace('\\', '/')
            log_violation(found[0], found[1], rel_path)

        # Prepare dashboard data
        total_violations, top_label, top_count = get_violations_summary()
        class_dist = get_class_distribution()
        recent = get_latest_violation()

        return render_template('index.html',
            result_image=filename,
            total_violations=total_violations,
            top_violation_label=top_label,
            top_violation_count=top_count,
            class_distribution=class_dist,
            recent_snapshot=recent
        )

    @app.route('/get_active_classes')
    def get_active_classes():
        return jsonify(list(active_violation_filters))

    @app.route('/set_active_classes', methods=['POST'])
    def set_active_classes():
        global active_violation_filters
        try:
            data = json.loads(request.data)
            active_violation_filters = set(data.get('classes', VIOLATION_CLASSES))
            return '', 204
        except Exception as e:
            return str(e), 400
