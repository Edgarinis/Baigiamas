# Configuration file for the project
from flask_login import UserMixin
VIDEO_SOURCE = 0 # 0 webcam or a file path
STREAM_ACTIVE = False
class User(UserMixin):
    pass