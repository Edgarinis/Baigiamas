from flask import Flask
from db import init_db
from routes import configure_routes
import os

app = Flask(__name__)
app.config['VIDEO_SOURCE'] = 0
app.config['STREAM_ACTIVE'] = False    # ← new

# Configure paths for image handling
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/snapshots'

# Ensure those folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

init_db()
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
