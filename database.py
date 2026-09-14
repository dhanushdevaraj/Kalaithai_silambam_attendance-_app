import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "silambam_attendance.db"

def get_connection():
    """Returns a SQLite connection with dict-like row accessibility."""
    conn = sqlite3.connect(DB_FILE, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password, salt="kalaithai_silambam_salt_2026"):
    """Hash password using SHA256 with salt."""
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_db():
    """Initialize database tables and default accounts."""
    conn = get_connection()
    c = conn.cursor()

    # Users Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'trainer',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Students Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reg_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            gender TEXT,
            phone TEXT,
            status TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Attendance Table
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            marked_by TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            UNIQUE(student_id, date)
        )
    """)

    # Seed Default Users (Admin & Trainer)
    seed_default_users(c)

    conn.commit()
    conn.close()

def seed_default_users(cursor):
    """Seed initial Admin and Trainer accounts if not existing."""
    default_users = [
        ('admin', 'admin123', 'Master Admin', 'admin'),
        ('trainer', 'trainer123', 'Head Trainer', 'trainer')
    ]
    for username, password, full_name, role in default_users:
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
        if cursor.fetchone()[0] == 0:
            pw_hash = hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                (username, pw_hash, full_name, role)
            )

# --- USER MANAGEMENT FUNCTIONS ---

def add_user(username, password, full_name, role='trainer'):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), full_name, role)
        )
        conn.commit()
        conn.close()
        return True, "User registered successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists!"

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, username, full_name, role, created_at FROM users ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user = c.fetchone()
    if user and user['username'] in ['admin', 'trainer']:
        conn.close()
        return False, "Protected system accounts cannot be deleted!"
    
    c.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True, "User deleted successfully!"

# --- STUDENT MANAGEMENT FUNCTIONS ---

def add_student(reg_no, name, category, gender, phone):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO students (reg_no, name, category, gender, phone) VALUES (?, ?, ?, ?, ?)",
            (reg_no, name, category, gender, phone)
        )
        conn.commit()
        conn.close()
        return True, "Student registered successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Registration Number already exists!"

def get_all_students(status='active'):
    conn = get_connection()
    c = conn.cursor()
    if status == 'all':
        c.execute("SELECT * FROM students ORDER BY name ASC")
    else:
        c.execute("SELECT * FROM students WHERE status = ? ORDER BY name ASC", (status,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_student(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id = ?", (student_id,))
    c.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True, "Student removed successfully!"

# --- ATTENDANCE FUNCTIONS ---

def mark_attendance(student_id, date_str, status, marked_by):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO attendance (student_id, date, status, marked_by)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(student_id, date) DO UPDATE SET
            status = excluded.status,
            marked_by = excluded.marked_by,
            timestamp = CURRENT_TIMESTAMP
    """, (student_id, date_str, status, marked_by))
    conn.commit()
    conn.close()

def get_attendance_by_date(date_str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.id, s.reg_no, s.name, s.category, 
               COALESCE(a.status, 'Not Marked') as status,
               a.marked_by, a.timestamp
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
        WHERE s.status = 'active'
        ORDER BY s.name ASC
    """, (date_str,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_individual_report(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT date, status, marked_by, timestamp
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
    """, (student_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_monthly_attendance_matrix(year_month):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT s.reg_no, s.name, a.date, a.status
        FROM students s
        JOIN attendance a ON s.id = a.student_id
        WHERE a.date LIKE ? AND s.status = 'active'
        ORDER BY s.name, a.date
    """, (f"{year_month}%",))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]