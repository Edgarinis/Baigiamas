import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        label TEXT,
        confidence REAL,
        snapshot_path TEXT
    )''')
    conn.commit()
    conn.close()

def log_violation(label, confidence, snapshot_path=None):
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO violations (timestamp, label, confidence, snapshot_path) VALUES (?, ?, ?, ?)",
              (timestamp, label, confidence, snapshot_path))
    conn.commit()
    conn.close()

def get_violations():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute("SELECT * FROM violations ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return rows
