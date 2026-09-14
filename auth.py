import streamlit as st
from database import get_connection, hash_password

def authenticate_user(username, password):
    """Authenticate user against database credentials."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    if user and user['password_hash'] == hash_password(password):
        return {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    return None

def login_required():
    """Ensure user is logged in before rendering protected views."""
    if "user" not in st.session_state or st.session_state.user is None:
        return False
    return True

def is_admin():
    """Check if current logged-in user is Admin."""
    return st.session_state.user and st.session_state.user.get("role") == "admin"