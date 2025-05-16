from flask import render_template, Response
from db import get_violations
from detector import generate_frames

def configure_routes(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/video_feed')
    def video_feed():
        return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @app.route('/violations')
    def violations():
        rows = get_violations()
        return render_template('violations.html', rows=rows)
