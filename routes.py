from flask import render_template, Response, request, redirect, url_for, jsonify, current_app
from detector import generate_frames
from db import get_violations, log_violation, get_violations_summary, get_class_distribution, get_latest_violation
from ultralytics import YOLO
import os, datetime, json, config

model = YOLO(r'C:\Users\cedga\Desktop\Baigiamas\runs\detect\train17\weights\best.pt')

VIOLATION_CLASSES = ['NO-Hardhat', 'NO-Mask', 'NO-Safety Vest']
active_violation_filters = set(VIOLATION_CLASSES)

def configure_routes(app):
    @app.route('/')
    def index():
        total, top_label, top_count = get_violations_summary()
        dist = get_class_distribution()
        recent = get_latest_violation()
        return render_template('index.html',
            total_violations=total,
            top_violation_label=top_label,
            top_violation_count=top_count,
            class_distribution=dist,
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

        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"img_{ts}.jpg"
        up = os.path.join(current_app.config['UPLOAD_FOLDER'], fname)
        res = os.path.join(current_app.config['RESULT_FOLDER'], fname)
        file.save(up)

        results = model(up, conf=0.3)
        results[0].save(filename=res)

        # log first violation
        for box in results[0].boxes.data.tolist():
            cls, conf = int(box[5]), box[4]
            lbl = results[0].names[cls]
            if lbl in VIOLATION_CLASSES:
                rel = os.path.relpath(res,'static').replace('\\','/')
                log_violation(lbl, float(conf), rel)
                break

        # re-gather dashboard
        total, top_label, top_count = get_violations_summary()
        dist = get_class_distribution()
        recent = get_latest_violation()

        return render_template('index.html',
            result_image=fname,
            total_violations=total,
            top_violation_label=top_label,
            top_violation_count=top_count,
            class_distribution=dist,
            recent_snapshot=recent
        )

    @app.route('/get_active_classes')
    def get_active_classes():
        return jsonify(list(active_violation_filters))

    @app.route('/set_active_classes', methods=['POST'])
    def set_active_classes():
        global active_violation_filters
        data = json.loads(request.data)
        active_violation_filters = set(data.get('classes', VIOLATION_CLASSES))
        return '', 204
    
    @app.route('/start_stream', methods=['POST'])
    def start_stream():
        config.STREAM_ACTIVE = True
        return ('', 204)

    @app.route('/stop_stream', methods=['POST'])
    def stop_stream():
        config.STREAM_ACTIVE = False
        return ('', 204)
    @app.route('/process_video', methods=['POST'])
    def process_video():
        file = request.files.get('video_file')
        if not file or file.filename == '':
            return redirect(url_for('index'))

        # 1) Save to your UPLOAD_FOLDER
        ts       = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"video_{ts}.mp4"
        savepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(savepath)

        # 2) Flip the source + start streaming immediately
        config.VIDEO_SOURCE  = savepath
        config.STREAM_ACTIVE = True

        # 3) Gather dashboard context as usual
        total, top_label, top_count = get_violations_summary()
        dist    = get_class_distribution()
        recent  = get_latest_violation()

        # 4) Render index.html with a flag to auto-kick off the stream
        return render_template('index.html',
            video_mode=True,
            total_violations    = total,
            top_violation_label = top_label,
            top_violation_count = top_count,
            class_distribution  = dist,
            recent_snapshot     = recent
        )