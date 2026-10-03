import streamlit as st
import pandas as pd
from datetime import date, datetime, time
import base64
from pathlib import Path
import io

from database import (
    init_db, add_user, get_all_users, delete_user,
    add_student, get_all_students, delete_student, clear_all_students,
    mark_attendance, get_attendance_by_date,
    get_individual_report, get_monthly_attendance_matrix,
    get_monthly_register_grid, generate_monthly_excel,
    bulk_import_students, get_student_sample_template
)
from auth import authenticate_user, is_admin
from translations import t, generate_whatsapp_link, format_whatsapp_phone

# Page Config
st.set_page_config(
    page_title="Kalaithai Silambam Attendance",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database
init_db()

# --- BATCH CONFIGURATION ---
BATCH_NAME = "Morning Batch"
BATCH_TIMING_STR = "06:30 AM - 08:30 AM"
BATCH_START_TIME = time(6, 30)
BATCH_END_TIME = time(8, 30)

def is_batch_window_open():
    """Checks if the current system time falls within the morning batch window (06:30 - 08:30)."""
    now_time = datetime.now().time()
    return BATCH_START_TIME <= now_time <= BATCH_END_TIME

def get_current_time_str():
    """Returns formatted current system time."""
    return datetime.now().strftime("%I:%M %p")

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
            background: rgba(14, 17, 23, 0.88);
            padding: 2.2rem;
            border-radius: 18px;
            margin-top: 1.5rem;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45);
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
            display: inline-block;
        }}

        .role-badge-trainer {{
            background-color: #00C853;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: bold;
            display: inline-block;
        }}

        /* Batch Badges and Status Banners */
        .batch-pill {{
            background: linear-gradient(135deg, #FF9800 0%, #FFD700 100%);
            color: #111;
            font-weight: 700;
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 13px;
            display: inline-block;
            margin-top: 6px;
            margin-bottom: 8px;
            box-shadow: 0 3px 10px rgba(255, 152, 0, 0.35);
        }}

        .batch-status-open {{
            background: linear-gradient(135deg, rgba(0, 200, 83, 0.18) 0%, rgba(0, 230, 118, 0.08) 100%);
            border: 1px solid #00C853;
            color: #E8F5E9;
            padding: 14px 18px;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 15px rgba(0, 200, 83, 0.15);
        }}

        .batch-status-closed {{
            background: linear-gradient(135deg, rgba(255, 75, 75, 0.18) 0%, rgba(255, 115, 0, 0.08) 100%);
            border: 1px solid #FF4B4B;
            color: #FFEBEE;
            padding: 14px 18px;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 15px rgba(255, 75, 75, 0.15);
        }}

        .batch-status-admin-override {{
            background: linear-gradient(135deg, rgba(156, 39, 176, 0.22) 0%, rgba(103, 58, 183, 0.12) 100%);
            border: 1px solid #BA68C8;
            color: #F3E5F5;
            padding: 14px 18px;
            border-radius: 12px;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 15px rgba(156, 39, 176, 0.2);
        }}

        .whatsapp-btn {{
            background-color: #25D366;
            color: white !important;
            padding: 6px 12px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            box-shadow: 0 3px 8px rgba(37, 211, 102, 0.3);
            transition: all 0.2s ease;
        }}
        .whatsapp-btn:hover {{
            background-color: #1EBE5D;
            transform: scale(1.02);
            color: white !important;
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
if "lang" not in st.session_state:
    st.session_state.lang = "ta"  # Default language is Tamil

def get_current_lang():
    return st.session_state.get("lang", "ta")

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- SIDEBAR COMPONENT ---

def render_sidebar():
    cur_lang = get_current_lang()
    with st.sidebar:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), use_container_width=True)
        else:
            st.markdown("### 🥋 KALAITHAI SILAMBAM")
            st.caption("KURUMPATTI")

        # Bilingual Language Switcher
        st.write("---")
        lang_choice = st.radio(
            "🌐 மொழி / Language",
            ["தமிழ்", "English"],
            horizontal=True,
            index=0 if cur_lang == "ta" else 1,
            key="language_toggle"
        )
        new_lang = "ta" if lang_choice == "தமிழ்" else "en"
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()

        st.write("---")
        if st.session_state.user:
            user = st.session_state.user
            role_class = "role-badge-admin" if user['role'] == 'admin' else "role-badge-trainer"
            st.markdown(f"### 👋 {user['full_name']}")
            st.markdown(f'<span class="{role_class}">{user["role"].upper()}</span>', unsafe_allow_html=True)
            
            # Batch Schedule & Status Widget
            is_open = is_batch_window_open()
            status_color = "#00E676" if is_open else "#FF5252"
            status_label = "🟢 OPEN" if is_open else "🔴 CLOSED"
            now_str = get_current_time_str()

            st.markdown(f"""
            <div style="margin-top: 12px; padding: 12px; background: rgba(255,255,255,0.06); border-radius: 12px; border: 1px solid rgba(255,255,255,0.12);">
                <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: #bbb;">{t("batch_timing", cur_lang)}</div>
                <div style="font-weight: 700; color: #FFD700; font-size: 14px; margin-top: 2px;">🌅 {BATCH_NAME}</div>
                <div style="font-size: 13px; color: #eee; margin-top: 2px;">⏰ {BATCH_TIMING_STR}</div>
                <div style="margin-top: 6px; font-size: 12px; font-weight: 600; color: {status_color};">
                    Window: {status_label} <span style="color: #aaa; font-weight: normal;">({now_str})</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("---")

            if st.button(t("nav_dashboard", cur_lang), use_container_width=True):
                navigate_to("dashboard")
            if st.button(t("nav_mark_attendance", cur_lang), use_container_width=True):
                navigate_to("mark_attendance")
            if st.button(t("nav_students_list", cur_lang), use_container_width=True):
                navigate_to("students")
            if st.button(t("nav_history", cur_lang), use_container_width=True):
                navigate_to("history")
            if st.button(t("nav_monthly_register", cur_lang), use_container_width=True):
                navigate_to("monthly_register")
            if st.button(t("nav_individual_report", cur_lang), use_container_width=True):
                navigate_to("report")

            # ADMIN ONLY MENU ITEMS
            if is_admin():
                st.write("---")
                st.markdown(f"**{t('admin_settings', cur_lang)}**")
                if st.button(t("nav_manage_students", cur_lang), use_container_width=True):
                    navigate_to("manage_students")
                if st.button(t("nav_manage_trainers", cur_lang), use_container_width=True):
                    navigate_to("manage_trainers")

            st.write("---")
            if st.button(t("nav_logout", cur_lang), use_container_width=True):
                st.session_state.user = None
                navigate_to("login")

# --- LOGIN PAGE ---

def render_login():
    cur_lang = get_current_lang()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        logo_path = Path("assets/logo.png")
        if logo_path.exists():
            st.image(str(logo_path), width=180)
            
        st.title(t("app_title", cur_lang))
        st.markdown(f'<div class="batch-pill">🌅 {BATCH_NAME}: {BATCH_TIMING_STR}</div>', unsafe_allow_html=True)
        st.caption(t("app_subtitle", cur_lang))

        # Language selector on Login Page
        lang_sel_login = st.radio("🌐 Language / மொழி", ["தமிழ்", "English"], horizontal=True, index=0 if cur_lang == "ta" else 1, key="login_lang_toggle")
        new_lang = "ta" if lang_sel_login == "தமிழ்" else "en"
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()

        st.write("---")

        username = st.text_input("Username / பயனர் பெயர்", key="login_user")
        password = st.text_input("Password / கடவுச்சொல்", type="password", key="login_pw")

        if st.button("🔐 LOGIN / உள்நுழை", use_container_width=True, type="primary"):
            user = authenticate_user(username, password)
            if user:
                st.session_state.user = user
                st.success(f"Welcome back, {user['full_name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password / தவறான பயனர் பெயர் அல்லது கடவுச்சொல்")

# --- DASHBOARD VIEW ---

def render_dashboard():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("nav_dashboard", cur_lang))
    today_str = str(date.today())
    now_str = get_current_time_str()
    is_open = is_batch_window_open()
    
    # Batch Schedule Notification Banner
    if is_open:
        st.markdown(f"""
        <div class="batch-status-open">
            <span style="font-size: 22px;">🟢</span>
            <div>
                <strong>Morning Batch Window ACTIVE ({BATCH_TIMING_STR})</strong><br>
                <small>Current Time: <strong>{now_str}</strong> • Morning batch attendance marking is open for trainers and admins.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        if is_admin():
            override_msg = "👑 <strong>Admin Override:</strong> As an Administrator, you can record or modify attendance at any time."
            banner_class = "batch-status-admin-override"
            icon = "👑"
        else:
            override_msg = "🔒 <strong>Marking Locked:</strong> Morning batch is from 6:30 AM to 8:30 AM only. Attendance marking is currently locked for trainers."
            banner_class = "batch-status-closed"
            icon = "⏰"

        st.markdown(f"""
        <div class="{banner_class}">
            <span style="font-size: 22px;">{icon}</span>
            <div>
                <strong>Morning Batch Window CLOSED ({BATCH_TIMING_STR})</strong><br>
                <small>Current Time: <strong>{now_str}</strong> • {override_msg}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    students = get_all_students()
    attendance_today = get_attendance_by_date(today_str)
    
    present_count = sum(1 for a in attendance_today if a['status'] == 'Present')
    absent_count = sum(1 for a in attendance_today if a['status'] == 'Absent')
    unmarked_count = sum(1 for a in attendance_today if a['status'] == 'Not Marked')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"👥 {t('total_active_students', cur_lang)}", len(students))
    c2.metric(f"✅ {t('present_today', cur_lang)}", present_count)
    c3.metric(f"❌ {t('absent_today', cur_lang)}", absent_count)
    c4.metric(f"⏳ {t('not_marked_today', cur_lang)}", unmarked_count)

    # WhatsApp Alert Quick Banner for Today's Absentees
    absent_students = [a for a in attendance_today if a['status'] == 'Absent']
    if absent_students:
        st.markdown("---")
        st.markdown(f"""
        <div style="background: rgba(37, 211, 102, 0.12); border: 1px solid #25D366; padding: 12px 18px; border-radius: 12px; margin-bottom: 12px;">
            <strong style="color: #25D366; font-size: 15px;">📱 {t('whatsapp_absentees_banner', cur_lang).format(count=len(absent_students))}</strong>
            <div style="margin-top: 6px; font-size: 13px; color: #ddd;">
                Click below to alert parents of absent students on WhatsApp in 1-click:
            </div>
        </div>
        """, unsafe_allow_html=True)

        wa_cols = st.columns(min(len(absent_students), 3) or 1)
        for idx, a_stu in enumerate(absent_students):
            wa_link = generate_whatsapp_link(a_stu.get('phone', ''), a_stu['name'], today_str, cur_lang)
            with wa_cols[idx % 3]:
                if wa_link:
                    st.markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">📱 {a_stu["name"]} ({a_stu["reg_no"]})</a>', unsafe_allow_html=True)
                else:
                    st.write(f"⚠️ {a_stu['name']} (No phone)")

    st.write("---")
    st.subheader(f"📅 {t('today_overview', cur_lang)} ({today_str})")
    
    if attendance_today:
        df = pd.DataFrame(attendance_today)
        df = df[['reg_no', 'name', 'batch', 'category', 'status', 'marked_by']]
        df.columns = ['Reg No', 'Student Name', 'Batch Timing', 'Category', 'Status', 'Marked By']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students registered yet. Go to 'Student Management' to add students!")

# --- MARK ATTENDANCE VIEW (WITH 1-CLICK WHATSAPP PARENT ALERTS) ---

def render_mark_attendance():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("nav_mark_attendance", cur_lang))

    col1, col2 = st.columns([1, 2])
    selected_date = col1.date_input(t("select_date", cur_lang), date.today())
    date_str = str(selected_date)

    attendance_data = get_attendance_by_date(date_str)
    
    if not attendance_data:
        st.warning("No active students available. Please add students first.")
        return

    # Check window & role permission
    is_open = is_batch_window_open()
    admin_override = is_admin()
    can_mark = is_open or admin_override
    now_str = get_current_time_str()

    if is_open:
        st.markdown(f"""
        <div class="batch-status-open">
            <span style="font-size: 22px;">🟢</span>
            <div>
                <strong>Morning Batch Window OPEN ({BATCH_TIMING_STR})</strong><br>
                <small>System Time: <strong>{now_str}</strong> • Attendance marking is enabled.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif admin_override:
        st.markdown(f"""
        <div class="batch-status-admin-override">
            <span style="font-size: 22px;">👑</span>
            <div>
                <strong>Admin Override Active (Morning Batch: {BATCH_TIMING_STR})</strong><br>
                <small>System Time: <strong>{now_str}</strong> • Batch window is closed for trainers, but as an Administrator you have override permission to mark attendance.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="batch-status-closed">
            <span style="font-size: 22px;">🔒</span>
            <div>
                <strong>Morning Batch Window CLOSED ({BATCH_TIMING_STR})</strong><br>
                <small>System Time: <strong>{now_str}</strong> • Attendance can only be marked during Morning Batch hours (6:30 AM – 8:30 AM). Contact Admin if changes are required.</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.write("---")

    # Bulk Attendance Actions
    if can_mark:
        c_btn1, c_btn2, _ = st.columns([1.2, 1.2, 2])
        if c_btn1.button(t("mark_all_present", cur_lang), use_container_width=True, type="secondary"):
            for item in attendance_data:
                mark_attendance(item['id'], date_str, "Present", st.session_state.user['username'], item.get('batch', f"Morning ({BATCH_TIMING_STR})"))
            st.success("All active students marked Present!")
            st.rerun()

        if c_btn2.button(t("mark_all_absent", cur_lang), use_container_width=True):
            for item in attendance_data:
                mark_attendance(item['id'], date_str, "Absent", st.session_state.user['username'], item.get('batch', f"Morning ({BATCH_TIMING_STR})"))
            st.success("All active students marked Absent!")
            st.rerun()
    else:
        st.info("ℹ️ Attendance marking buttons are disabled outside the morning window (06:30 AM - 08:30 AM).")

    st.write("---")
    st.subheader(f"{t('student_roster', cur_lang)} — 🌅 {BATCH_NAME} ({BATCH_TIMING_STR})")

    for student in attendance_data:
        cols = st.columns([1, 2.5, 1.5, 1.5, 1.5, 2])
        cols[0].write(f"**{student['reg_no']}**")
        cols[1].write(f"**{student['name']}** _({student['category']})_")

        current_status = student['status']
        student_batch = student.get('batch', f"Morning ({BATCH_TIMING_STR})")
        
        if can_mark:
            if cols[2].button(f"✅ {t('present', cur_lang)}", key=f"p_{student['id']}"):
                mark_attendance(student['id'], date_str, "Present", st.session_state.user['username'], student_batch)
                st.rerun()

            if cols[3].button(f"❌ {t('absent', cur_lang)}", key=f"a_{student['id']}"):
                mark_attendance(student['id'], date_str, "Absent", st.session_state.user['username'], student_batch)
                st.rerun()
        else:
            cols[2].write("🔒 _Locked_")
            cols[3].write("🔒 _Locked_")

        # Status Tag
        status_label = "🟢 Present" if current_status == "Present" else ("🔴 Absent" if current_status == "Absent" else "⚪ Not Marked")
        cols[4].write(status_label)

        # 1-Click WhatsApp Parent Alert when Absent
        if current_status == "Absent":
            wa_link = generate_whatsapp_link(student.get('phone', ''), student['name'], date_str, cur_lang)
            if wa_link:
                cols[5].markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">📱 WhatsApp</a>', unsafe_allow_html=True)
            else:
                cols[5].caption("No phone saved")
        else:
            cols[5].write("")

# --- MONTHLY ATTENDANCE REGISTER (GRID + EXCEL DOWNLOAD) ---

def render_monthly_register():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("monthly_register_title", cur_lang))
    st.caption("Standard 1-to-31 Master Attendance Grid with instant Excel (.xlsx) and CSV export.")

    c_m1, c_m2, _ = st.columns([1.5, 1.5, 1])
    current_year = date.today().year
    current_month = date.today().month

    with c_m1:
        sel_year = st.selectbox("Year / ஆண்டு", list(range(current_year - 2, current_year + 3)), index=2)
    with c_m2:
        month_names = ["01 - January", "02 - February", "03 - March", "04 - April", "05 - May", "06 - June",
                       "07 - July", "08 - August", "09 - September", "10 - October", "11 - November", "12 - December"]
        sel_month_idx = st.selectbox("Month / மாதம்", list(range(1, 13)), index=current_month - 1, format_func=lambda x: month_names[x - 1])

    year_month_str = f"{sel_year:04d}-{sel_month_idx:02d}"

    grid_df, day_cols = get_monthly_register_grid(year_month_str)

    if grid_df.empty:
        st.warning(t("no_attendance_for_month", cur_lang))
        st.info("Ensure students are enrolled and attendance is marked for this month.")
        return

    # Download Buttons (Excel & CSV)
    st.write("---")
    d_col1, d_col2, _ = st.columns([1.8, 1.5, 1])

    with d_col1:
        try:
            excel_bytes = generate_monthly_excel(grid_df, year_month_str, BATCH_NAME)
            st.download_button(
                label=t("download_excel", cur_lang),
                data=excel_bytes,
                file_name=f"Kalaithai_Silambam_Register_{year_month_str}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel generation error: {e}")

    with d_col2:
        csv_bytes = grid_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=t("download_csv", cur_lang),
            data=csv_bytes,
            file_name=f"Kalaithai_Silambam_Register_{year_month_str}.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.write("---")
    st.subheader(f"📊 Register Grid — {year_month_str} (P = Present, A = Absent, - = No Class)")

    # Color highlight for dataframe
    def color_grid(val):
        if val == 'P':
            return 'background-color: #065F46; color: #D1FAE5; font-weight: bold; text-align: center;'
        elif val == 'A':
            return 'background-color: #991B1B; color: #FEE2E2; font-weight: bold; text-align: center;'
        elif val == '-':
            return 'color: #6B7280; text-align: center;'
        return ''

    styled_df = grid_df.style.map(color_grid, subset=day_cols)
    st.dataframe(styled_df, use_container_width=True)

# --- STUDENTS LIST VIEW ---

def render_students():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("nav_students_list", cur_lang))
    st.caption(f"Default Batch: 🌅 {BATCH_NAME} ({BATCH_TIMING_STR})")
    
    students = get_all_students()
    if students:
        df = pd.DataFrame(students)[['reg_no', 'name', 'batch', 'category', 'gender', 'phone', 'status']]
        df.columns = ['Reg No', 'Full Name', 'Batch Timing', 'Category', 'Gender', 'Phone', 'Status']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No students found in system database.")

# --- ATTENDANCE HISTORY VIEW ---

def render_history():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("nav_history", cur_lang))

    selected_date = st.date_input(t("select_date", cur_lang), date.today())
    date_str = str(selected_date)

    data = get_attendance_by_date(date_str)
    if data:
        st.subheader(f"📅 Attendance for {date_str}")
        
        # Check absentees for WhatsApp alerts
        absentees = [d for d in data if d['status'] == 'Absent']
        if absentees:
            st.markdown(f"##### 📱 {t('whatsapp_absentees_banner', cur_lang).format(count=len(absentees))}")
            w_cols = st.columns(min(len(absentees), 3) or 1)
            for idx, a_stu in enumerate(absentees):
                wa_link = generate_whatsapp_link(a_stu.get('phone', ''), a_stu['name'], date_str, cur_lang)
                with w_cols[idx % 3]:
                    if wa_link:
                        st.markdown(f'<a href="{wa_link}" target="_blank" class="whatsapp-btn">📱 WhatsApp: {a_stu["name"]}</a>', unsafe_allow_html=True)

        st.write("---")
        df = pd.DataFrame(data)[['reg_no', 'name', 'batch', 'category', 'status', 'marked_by', 'timestamp']]
        df.columns = ['Reg No', 'Student Name', 'Batch Timing', 'Category', 'Status', 'Marked By', 'Last Updated']
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("No attendance records found for selected date.")

# --- INDIVIDUAL REPORT VIEW ---

def render_report():
    render_sidebar()
    cur_lang = get_current_lang()
    st.title(t("nav_individual_report", cur_lang))

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
        df = pd.DataFrame(records)[['date', 'batch', 'status', 'marked_by', 'timestamp']]
        df.columns = ['Date', 'Batch Timing', 'Status', 'Marked By', 'Timestamp']
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No attendance records logged for this student.")

# --- ADMIN: STUDENT MANAGEMENT (MANUAL + EXCEL BULK UPLOAD + CLEAR DB) ---

def render_manage_students():
    render_sidebar()
    cur_lang = get_current_lang()
    if not is_admin():
        st.error("⚠️ Permission Denied: Admin access required.")
        return

    st.title(t("nav_manage_students", cur_lang))

    tab1, tab2, tab3 = st.tabs([
        f"➕ {t('add_new_student', cur_lang)}",
        f"📁 {t('bulk_upload_tab', cur_lang)}",
        f"📋 {t('manage_students_tab', cur_lang)}"
    ])

    # TAB 1: ADD STUDENT MANUALLY
    with tab1:
        with st.form("add_student_form", clear_on_submit=True):
            st.subheader(t("add_new_student", cur_lang))
            c1, c2 = st.columns(2)
            reg_no = c1.text_input(t("reg_no", cur_lang))
            name = c2.text_input(t("student_name", cur_lang))
            category = c1.selectbox(t("category", cur_lang), ["Sub-Junior", "Junior", "Senior", "Super Senior"], index=1)
            gender = c2.selectbox(t("gender", cur_lang), ["Male", "Female", "Other"])
            batch = c1.selectbox(t("batch", cur_lang), [f"Morning ({BATCH_TIMING_STR})"], index=0)
            phone = c2.text_input(t("phone", cur_lang), placeholder="10-digit mobile number")

            submit = st.form_submit_button(t("register_student_btn", cur_lang), type="primary", use_container_width=True)
            if submit:
                if reg_no.strip() and name.strip():
                    success, msg = add_student(reg_no.strip(), name.strip(), category, gender, phone.strip(), batch)
                    if success:
                        st.success(f"✅ {msg}")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.warning("Registration Number and Name are required!")

    # TAB 2: EXCEL / CSV BULK UPLOAD
    with tab2:
        st.subheader("📁 Upload Student List via Excel (.xlsx) or CSV")
        st.caption("Upload your student roster directly. Columns supported: Reg No, Student Name, Category, Gender, Phone, Batch.")

        # Download Template buttons
        template_df = get_student_sample_template()
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False, sheet_name="Students")
            st.download_button(
                label="📥 Download Sample Excel Template (.xlsx)",
                data=buf.getvalue(),
                file_name="silambam_students_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with b_c2:
            st.download_button(
                label="📥 Download Sample CSV Template (.csv)",
                data=template_df.to_csv(index=False).encode("utf-8"),
                file_name="silambam_students_template.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.write("---")
        uploaded_file = st.file_uploader("Choose Excel or CSV file", type=["xlsx", "xls", "csv"])
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    import_df = pd.read_csv(uploaded_file)
                else:
                    import_df = pd.read_excel(uploaded_file)

                st.markdown("##### 🔍 Preview Uploaded Data:")
                st.dataframe(import_df, use_container_width=True)
                st.write(f"Detected **{len(import_df)}** student rows.")

                if st.button("🚀 Confirm & Import Students into Database", type="primary", use_container_width=True):
                    ok, cnt, msg = bulk_import_students(import_df, default_batch=f"Morning ({BATCH_TIMING_STR})")
                    if ok:
                        st.success(f"🎉 {msg}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"Import error: {msg}")
            except Exception as e:
                st.error(f"Error reading uploaded file: {e}")

    # TAB 3: MANAGE / DELETE STUDENTS & CLEAR DATABASE
    with tab3:
        st.subheader("Manage Active Students")
        students = get_all_students()
        if students:
            for s in students:
                cols = st.columns([1.5, 3, 2, 1.5])
                cols[0].write(f"**{s['reg_no']}**")
                cols[1].write(f"**{s['name']}** _({s['category']})_<br><small style='color: #FFD700;'>🌅 {s.get('batch', 'Morning (' + BATCH_TIMING_STR + ')')}</small>", unsafe_allow_html=True)
                cols[2].write(f"📞 {s['phone'] or 'N/A'}")
                if cols[3].button("🗑️ Remove", key=f"del_std_{s['id']}"):
                    delete_student(s['id'])
                    st.success("Student removed.")
                    st.rerun()
        else:
            st.info("No students enrolled currently. Use the tabs above to add students!")

        st.write("---")
        # Danger Zone: Clear Entire Database
        with st.expander(t("clear_db_title", cur_lang), expanded=False):
            st.warning("⚠️ This will permanently delete ALL student profiles and all historical attendance records.")
            confirm_chk = st.checkbox(t("clear_db_confirm", cur_lang), key="clear_all_confirm_box")
            if st.button(t("clear_db_btn", cur_lang), type="secondary", key="clear_all_execute_btn"):
                if confirm_chk:
                    clear_all_students()
                    st.success("All students and attendance records have been cleared from database.")
                    st.rerun()
                else:
                    st.warning("Please check the confirmation box first.")

# --- ADMIN: TRAINER MANAGEMENT ---

def render_manage_trainers():
    render_sidebar()
    cur_lang = get_current_lang()
    if not is_admin():
        st.error("⚠️ Permission Denied: Admin access required.")
        return

    st.title(t("nav_manage_trainers", cur_lang))

    with st.form("add_user_form", clear_on_submit=True):
        st.subheader("Create Trainer / Admin Account")
        c1, c2 = st.columns(2)
        username = c1.text_input("Username")
        password = c2.text_input("Password", type="password")
        full_name = c1.text_input("Full Name")
        role = c2.selectbox("Account Role", ["trainer", "admin"])

        submit = st.form_submit_button("➕ Create Account", type="primary", use_container_width=True)
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
            "monthly_register": render_monthly_register,
            "report": render_report,
            "manage_students": render_manage_students,
            "manage_trainers": render_manage_trainers,
        }
        page_func = pages.get(st.session_state.page, render_dashboard)
        page_func()

if __name__ == "__main__":
    main()