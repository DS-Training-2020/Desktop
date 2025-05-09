import sqlite3
import bcrypt
from datetime import datetime
import pytz
import os

DATABASE_NAME = "appointments.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        # Create users table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
        """)
        
        # Create appointments table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            appointment_type TEXT NOT NULL,
            sub_type TEXT NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'confirmed',
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        # Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_user_id ON appointments (user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments (date)")
        
        # Insert sample data if tables are empty
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            sample_users = [
                ("user1", "John Doe", hash_password("password1"), "user"),
                ("user2", "Jane Smith", hash_password("password2"), "user"),
                ("admin", "Admin User", hash_password("admin123"), "admin")
            ]
            conn.executemany(
                "INSERT INTO users (username, name, password, role) VALUES (?, ?, ?, ?)",
                sample_users
            )
            
        if conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] == 0:
            user_id = conn.execute("SELECT id FROM users WHERE username = 'user1'").fetchone()[0]
            sample_appointment = (
                user_id,
                "Consultation",
                "Dental consult",
                datetime(2023, 12, 15, 10, 0).isoformat(),
                "confirmed",
                datetime.now(pytz.utc).isoformat()
            )
            conn.execute(
                """INSERT INTO appointments 
                (user_id, appointment_type, sub_type, date, status, created_at) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                sample_appointment
            )
        
        conn.commit()

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(password, hashed):
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def get_user(username):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        ).fetchone()
        return dict(row) if row else None

def verify_user(username, password):
    user = get_user(username)
    if user and check_password(password, user["password"]):
        return user
    return None

def register_user(username, name, password, role="user"):
    try:
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO users (username, name, password, role) VALUES (?, ?, ?, ?)",
                (username, name, hash_password(password), role)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def create_appointment(username, appointment_type, sub_type, date):
    with get_db_connection() as conn:
        user_id = conn.execute(
            "SELECT id FROM users WHERE username = ?", 
            (username,)
        ).fetchone()[0]
        
        conn.execute(
            """INSERT INTO appointments 
            (user_id, appointment_type, sub_type, date, status, created_at) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                appointment_type,
                sub_type,
                date.isoformat(),
                "confirmed",
                datetime.now(pytz.utc).isoformat()
            )
        )
        conn.commit()
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]

def get_user_appointments(username):
    with get_db_connection() as conn:
        rows = conn.execute(
            """SELECT a.*, u.username 
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            WHERE u.username = ?
            ORDER BY a.date""",
            (username,)
        ).fetchall()
        return [dict(row) for row in rows]

def get_all_appointments():
    with get_db_connection() as conn:
        rows = conn.execute(
            """SELECT a.*, u.username 
            FROM appointments a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.date"""
        ).fetchall()
        return [dict(row) for row in rows]

def update_appointment(appointment_id, appointment_type, sub_type, date):
    with get_db_connection() as conn:
        conn.execute(
            """UPDATE appointments 
            SET appointment_type = ?, sub_type = ?, date = ?
            WHERE id = ?""",
            (appointment_type, sub_type, date.isoformat(), appointment_id)
        )
        conn.commit()

def delete_appointment(appointment_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()

# Initialize database when this module is imported
init_db()