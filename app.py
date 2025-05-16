from flask import Flask
from db import init_db
from routes import configure_routes

app = Flask(__name__)
init_db()
configure_routes(app)

if __name__ == '__main__':
    app.run(debug=True)
