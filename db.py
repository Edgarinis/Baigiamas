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

def get_violations_summary():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM violations")
    total = c.fetchone()[0]

    c.execute("SELECT label, COUNT(*) as count FROM violations GROUP BY label ORDER BY count DESC LIMIT 1")
    top = c.fetchone() or ('-', 0)

    conn.close()
    return total, top[0], top[1]

def get_class_distribution():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute("SELECT label, COUNT(*) FROM violations GROUP BY label")
    results = dict(c.fetchall())
    conn.close()
    return results

def get_latest_violation():
    conn = sqlite3.connect('violations.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM violations ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row