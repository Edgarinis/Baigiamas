import os

from flask import Flask
from flask_login import LoginManager
from config import User
from src.db import init_db, get_user_by_id
from src.routes import configure_routes

# -----------------------------------------------------------------------------
# 1) Create the Flask app and its configuration
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY']    = '741852963'
app.config['VIDEO_SOURCE']  = 0      # 0 = webcam by default
app.config['STREAM_ACTIVE'] = False  # start-withinactive

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/snapshots'
# make sure those exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)

#Initialize db, routes
init_db()
configure_routes(app)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # redirect if @login_required

@login_manager.user_loader
def load_user(user_id):

    row = get_user_by_id(int(user_id))
    if not row:
        return None
    u = User()
    u.id       = row['id']
    u.username = row['username']
    u.role     = row['role']
    return u


if __name__ == '__main__':
    app.run(debug=True)
