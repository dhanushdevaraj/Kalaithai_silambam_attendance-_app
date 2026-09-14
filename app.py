import streamlit as st
import pandas as pd
from datetime import date
import base64
from pathlib import Path

from database import (
    init_db, add_user, get_all_users, delete_user,
    add_student, get_all_students, delete_student,
    mark_attendance, get_attendance_by_date,
    get_individual_report, get_monthly_attendance_matrix
)
from auth import authenticate_user, is_admin

# Page Config
st.set_page_config(
    page_title="Kalaithai Silambam Attendance",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# --- CSS STYLING & BACKGROUND LOADERS ---

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def apply_custom_styles():
    bg_file = Path("assets/background.jpg")
    bg_css = ""
    if bg_file.exists():
        bin_str = get_base64_of_bin_file(bg_file)
        bg_css = f"""
        .stApp {{
            background-image: url("data:image/jpeg;base64,{bin_str}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        .stApp > header {{ background: transparent; }}
        """

    # Overlay & Card Style Injection
    st.markdown(f"""
        <style>
        {bg_css}
        
        /* Dark Translucent Overlay for Readable Content */
        .block-container {{
            background: rgba(14, 17, 23, 0.82);
            padding: 2.5rem;
            border-radius: 18px;
            margin-top: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            backdrop-filter: blur(8px);
        }}

        /* Heading & Typography Styling */
        h1, h2, h3 {{
            color: #FFD700 !important;
            font-weight: 700 !important;
        }}

        .role-badge-admin {{
            background-color: #FF4B4B;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
        }}

        .role-badge-trainer {{
            background-color: #00C853;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
        }}

        /* Buttons Styling */
        .stButton > button {{
            border-radius: 10px;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- SESSION STATE INITIALIZATION ---

if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- SIDEBAR COMPONENT ---

def render_sidebar():
    with st.sidebar:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("### 🥋 KALAITHAI SILAMBAM")
        
        st.write("---")
        if st.session_state.user:
            user = st.session_state.user
            role_class = "role-badge-admin" if user['role'] == 'admin' else "role-badge-trainer"
            st.markdown(f"### 👋 {user['full_name']}")
            st.markdown(f'<span class="{role_class}">{user["role"].upper()}</span>', unsafe_allow_html=True)
            st.write("---")

            if st.button("📊 Dashboard", use_container_width=True):
                navigate_to("dashboard")
            if st.button("📝 Mark Attendance", use_container_width=True):
                navigate_to("mark_attendance")
            if st.button("👥 Students List", use_container_width=True):
                navigate_to("students")
            if st.button("📅 Attendance History", use_container_width=True):
                navigate_to("history")
            if st.button("📈 Individual Report", use_container_width=True):
                navigate_to("report")

            # ADMIN ONLY MENU ITEMS
            if is_admin():
                st.write("---")
                st.markdown("**Admin Settings**")
                if st.button("➕ Student Management", use_container_width=True):
                    navigate_to("manage_students")
                if st.button("🔐 Manage Trainers", use_container_width=True):
                    navigate_to("manage_trainers")

            st.write("---")
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user = None
                navigate_to("login")

# --- LOGIN PAGE ---

def render_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), width=180)
            
        st.title("KALAITHAI SILAMBAM")
        st.subheader("KURUMPATTI")
        st.caption("Student Attendance Management System")
        st.write("---")

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pw")

        if st.button("🔐 LOGIN", use_container_width=True):
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                st.success(f"Welcome back, {user['full_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password")

# --- DASHBOARD VIEW ---

def render_dashboard():
    render_sidebar()
    st.title("📊 Attendance Dashboard")
    today_str = str(date.today())
    
    students = get_all_students()
    attendance_today = get_attendance_by_date(today_str)
    
    present_count = sum(1 for a in attendance_today if a['status'] == 'Present')
    absent_count = sum(1 for a in attendance_today if a['status'] == 'Absent')
    unmarked_count = sum(1 for a in attendance_today if a['status'] == 'Not Marked')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("👥 Total Active Students", len(students))
    c2.metric("✅ Present Today", present_count)
    c3.metric("❌ Absent Today", absent_count)
    c4.metric("⏳ Not Marked Today", unmarked_count)

    st.write("---")
    st.subheader(f"📅 Today's Attendance Overview ({today_str})")
    
    if attendance_today:
        df = pd.DataFrame(attendance_today)
        df = df[['reg_no', 'name', 'category', 'status', 'marked_by']]
        df.columns = ['Reg No', 'Student Name', 'Category', 'Status', 'Marked By']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students registered yet.")

# --- MARK ATTENDANCE VIEW ---

def render_mark_attendance():
    render_sidebar()
    st.title("📝 Mark Student Attendance")

    col1, col2 = st.columns([1, 2])
    selected_date = col1.date_input("Select Date", date.today())
    date_str = str(selected_date)

    attendance_data = get_attendance_by_date(date_str)
    
    if not attendance_data:
        st.warning("No active students available to mark attendance.")
        return

    st.write("---")
    c_btn1, c_btn2, _ = st.columns([1, 1, 2])
    
    # Bulk Mark Present
    if c_btn1.button("✅ Mark All Present", use_container_width=True):
        for item in attendance_data:
            mark_attendance(item['id'], date_str, "Present", st.session_state.user['username'])
        st.success("All active students marked Present!")
        st.rerun()

    # Bulk Mark Absent
    if c_btn2.button("❌ Mark All Absent", use_container_width=True):
        for item in attendance_data:
            mark_attendance(item['id'], date_str, "Absent", st.session_state.user['username'])
        st.success("All active students marked Absent!")
        st.rerun()

    st.write("---")
    st.subheader("Student Roster")

    for student in attendance_data:
        cols = st.columns([1, 3, 2, 2, 2])
        cols[0].write(f"**{student['reg_no']}**")
        cols[1].write(f"{student['name']} _({student['category']})_")

        current_status = student['status']
        
        # Individual Attendance Buttons
        if cols[2].button("✅ Present", key=f"p_{student['id']}"):
            mark_attendance(student['id'], date_str, "Present", st.session_state.user['username'])
            st.rerun()

        if cols[3].button("❌ Absent", key=f"a_{student['id']}"):
            mark_attendance(student['id'], date_str, "Absent", st.session_state.user['username'])
            st.rerun()

        # Status Tag
        status_color = "🟢 Present" if current_status == "Present" else ("🔴 Absent" if current_status == "Absent" else "⚪ Not Marked")
        cols[4].write(f"**Status:** {status_color}")

# --- STUDENTS LIST VIEW ---

def render_students():
    render_sidebar()
    st.title("👥 Student Directory")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students)[['reg_no', 'name', 'category', 'gender', 'phone', 'status']]
        df.columns = ['Reg No', 'Full Name', 'Category', 'Gender', 'Phone', 'Status']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students found in system database.")

# --- ATTENDANCE HISTORY VIEW ---

def render_history():
    render_sidebar()
    st.title("📅 Attendance History")

    selected_date = st.date_input("Select Date", date.today())
    date_str = str(selected_date)

    data = get_attendance_by_date(date_str)
    if data:
        df = pd.DataFrame(data)[['reg_no', 'name', 'category', 'status', 'marked_by', 'timestamp']]
        df.columns = ['Reg No', 'Student Name', 'Category', 'Status', 'Marked By', 'Last Updated']
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No attendance records found for selected date.")

# --- INDIVIDUAL REPORT VIEW ---

def render_report():
    render_sidebar()
    st.title("📈 Individual Attendance Report")

    students = get_all_students()
    if not students:
        st.warning("No students available.")
        return

    student_dict = {f"{s['reg_no']} - {s['name']}": s['id'] for s in students}
    selected_name = st.selectbox("Select Student", list(student_dict.keys()))
    student_id = student_dict[selected_name]

    records = get_individual_report(student_id)
    if records:
        total_classes = len(records)
        present_days = sum(1 for r in records if r['status'] == 'Present')
        percentage = (present_days / total_classes * 100) if total_classes > 0 else 0

        c1, c2, c3 = st.columns(3)
        c1.metric("Total Classes Conducted", total_classes)
        c2.metric("Classes Attended", present_days)
        c3.metric("Attendance Percentage", f"{percentage:.1f}%")

        st.write("---")
        df = pd.DataFrame(records)
        df.columns = ['Date', 'Status', 'Marked By', 'Timestamp']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance records logged for this student.")

# --- ADMIN: STUDENT MANAGEMENT ---

def render_manage_students():
    render_sidebar()
    if not is_admin():
        st.error("⚠️ Permission Denied: Admin access required.")
        return

    st.title("➕ Student Management (Admin)")

    with st.form("add_student_form"):
        st.subheader("Add New Student")
        c1, c2 = st.columns(2)
        reg_no = c1.text_input("Registration No (Unique)")
        name = c2.text_input("Student Name")
        category = c1.selectbox("Category", ["Sub-Junior", "Junior", "Senior", "Super Senior"])
        gender = c2.selectbox("Gender", ["Male", "Female", "Other"])
        phone = st.text_input("Contact Phone Number")

        submit = st.form_submit_button("➕ Register Student")
        if submit:
            if reg_no and name:
                success, msg = add_student(reg_no, name, category, gender, phone)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("Registration Number and Name are required!")

    st.write("---")
    st.subheader("Manage Active Students")
    students = get_all_students()
    for s in students:
        cols = st.columns([2, 3, 2, 2])
        cols[0].write(f"**{s['reg_no']}**")
        cols[1].write(f"{s['name']} _({s['category']})_")
        cols[2].write(s['phone'])
        if cols[3].button("🗑️ Remove", key=f"del_std_{s['id']}"):
            delete_student(s['id'])
            st.success("Student removed.")
            st.rerun()

# --- ADMIN: TRAINER MANAGEMENT ---

def render_manage_trainers():
    render_sidebar()
    if not is_admin():
        st.error("⚠️ Permission Denied: Admin access required.")
        return

    st.title("🔐 Manage Trainers & Accounts (Admin)")

    with st.form("add_user_form"):
        st.subheader("Create Trainer / Admin Account")
        c1, c2 = st.columns(2)
        username = c1.text_input("Username")
        password = c2.text_input("Password", type="password")
        full_name = c1.text_input("Full Name")
        role = c2.selectbox("Account Role", ["trainer", "admin"])

        submit = st.form_submit_button("➕ Create Account")
        if submit:
            if username and password and full_name:
                success, msg = add_user(username, password, full_name, role)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            else:
                st.warning("All fields are required!")

    st.write("---")
    st.subheader("Registered Accounts")
    users = get_all_users()
    for u in users:
        cols = st.columns([2, 3, 2, 2])
        cols[0].write(f"**{u['username']}**")
        cols[1].write(f"{u['full_name']}")
        cols[2].write(f"`{u['role'].upper()}`")
        if cols[3].button("🗑️ Delete", key=f"del_usr_{u['id']}"):
            success, msg = delete_user(u['id'])
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- MAIN ROUTER ---

def main():
    if st.session_state.user is None:
        render_login()
    else:
        pages = {
            "dashboard": render_dashboard,
            "mark_attendance": render_mark_attendance,
            "students": render_students,
            "history": render_history,
            "report": render_report,
            "manage_students": render_manage_students,
            "manage_trainers": render_manage_trainers,
        }
        page_func = pages.get(st.session_state.page, render_dashboard)
        page_func()

if __name__ == "__main__":
    main()