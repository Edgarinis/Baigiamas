import sqlite3, datetime
from werkzeug.security import generate_password_hash, check_password_hash


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
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
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

def add_user(username: str, password: str, role: str = 'viewer'):
    pw_hash = generate_password_hash(password)
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (username,password_hash,role) VALUES (?,?,?)',
              (username, pw_hash, role))
    conn.commit()
    conn.close()

def get_user_by_username(username: str):
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute('SELECT id,username,password_hash,role FROM users WHERE username=?', (username,))
    row = c.fetchone(); conn.close()
    if not row:
        return None
    uid, user, pw_hash, role = row
    return {'id': uid, 'username': user, 'password_hash': pw_hash, 'role': role}

def verify_user(username: str, password: str):
    u = get_user_by_username(username)
    if u and check_password_hash(u['password_hash'], password):
        return u
    return None

def get_user_by_id(uid: int):
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute('SELECT id, username, role FROM users WHERE id = ?', (uid,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {'id': row[0], 'username': row[1], 'role': row[2]}