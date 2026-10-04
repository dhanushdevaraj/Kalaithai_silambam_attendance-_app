import streamlit as st
import unicodedata
import hashlib
from database import get_connection, hash_password

def clean_input(val):
    """Normalize input strings, removing invisible characters and extra whitespace."""
    if not val:
        return ""
    text = unicodedata.normalize("NFKC", str(val))
    # Remove zero-width spaces, non-breaking spaces, and trim
    text = text.replace('\xa0', ' ').replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
    return text.strip()

def authenticate_user(username, password):
    """Authenticate user against database credentials with robust mobile space/case handling."""
    if not username or not password:
        return None
        
    clean_username = clean_input(username).lower()
    clean_password = clean_input(password)

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE LOWER(TRIM(username)) = ?", (clean_username,))
    user = c.fetchone()

    if user:
        expected_hash = user['password_hash']
        # 1. Salted SHA256 (Default standard)
        if hash_password(clean_password) == expected_hash:
            conn.close()
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        # 2. Raw SHA256 without salt fallback
        if hashlib.sha256(clean_password.encode()).hexdigest() == expected_hash:
            try:
                c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(clean_password), user['id']))
                conn.commit()
            except Exception:
                pass
            conn.close()
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }
        # 3. Direct plaintext match fallback
        if clean_password == expected_hash:
            try:
                c.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hash_password(clean_password), user['id']))
                conn.commit()
            except Exception:
                pass
            conn.close()
            return {
                "id": user["id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"]
            }

    # 4. Built-in Emergency Recovery for Default Credentials
    # Guarantees user is never locked out of Admin or Trainer on fresh/restarted cloud deployments
    if clean_username == "admin" and clean_password == "admin123":
        try:
            if user:
                c.execute("UPDATE users SET password_hash = ?, role = 'admin' WHERE id = ?", 
                          (hash_password("admin123"), user['id']))
            else:
                c.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                          ('admin', hash_password('admin123'), 'Master Admin', 'admin'))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()
        return {
            "id": user["id"] if user else 1,
            "username": "admin",
            "full_name": user["full_name"] if user else "Master Admin",
            "role": "admin"
        }

    if clean_username == "trainer" and clean_password == "trainer123":
        try:
            if user:
                c.execute("UPDATE users SET password_hash = ?, role = 'trainer' WHERE id = ?", 
                          (hash_password("trainer123"), user['id']))
            else:
                c.execute("INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                          ('trainer', hash_password('trainer123'), 'Head Trainer', 'trainer'))
            conn.commit()
        except Exception:
            pass
        finally:
            conn.close()
        return {
            "id": user["id"] if user else 2,
            "username": "trainer",
            "full_name": user["full_name"] if user else "Head Trainer",
            "role": "trainer"
        }

    conn.close()
    return None

def login_required():
    """Ensure user is logged in before rendering protected views."""
    if "user" not in st.session_state or st.session_state.user is None:
        return False
    return True

def is_admin():
    """Check if current logged-in user is Admin."""
    return st.session_state.user and st.session_state.user.get("role") == "admin"