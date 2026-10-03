"""
Bilingual Translations (Tamil & English) and WhatsApp Utility
for Kalaithai Silambam, Kurumpatti
"""

import urllib.parse

TRANSLATIONS = {
    # App & Navigation
    "app_title": {
        "ta": "கலைத்தாய் சிலம்பம், குரும்பட்டி",
        "en": "Kalaithai Silambam, Kurumpatti"
    },
    "app_subtitle": {
        "ta": "மாணவர் வருகை பதிவு & மேலாண்மை தளம்",
        "en": "Student Attendance Management System"
    },
    "nav_dashboard": {
        "ta": "📊 முகப்பு பலகை",
        "en": "📊 Dashboard"
    },
    "nav_mark_attendance": {
        "ta": "📝 வருகை பதிவு",
        "en": "📝 Mark Attendance"
    },
    "nav_students_list": {
        "ta": "👥 மாணவர்கள் பட்டியல்",
        "en": "👥 Students List"
    },
    "nav_history": {
        "ta": "📅 வருகை வரலாறு",
        "en": "📅 Attendance History"
    },
    "nav_monthly_register": {
        "ta": "📑 மாதாந்திர பதிவேடு",
        "en": "📑 Monthly Register"
    },
    "nav_individual_report": {
        "ta": "📈 தனிநபர் அறிக்கை",
        "en": "📈 Individual Report"
    },
    "nav_manage_students": {
        "ta": "➕ மாணவர் நிர்வாகம்",
        "en": "➕ Student Management"
    },
    "nav_manage_trainers": {
        "ta": "🔐 பயிற்சியாளர் கணக்குகள்",
        "en": "🔐 Manage Trainers"
    },
    "nav_logout": {
        "ta": "🚪 வெளியேறு",
        "en": "🚪 Logout"
    },
    "admin_settings": {
        "ta": "நிர்வாக அமைப்புகள் (Admin)",
        "en": "Admin Settings"
    },

    # Batch & Time
    "batch_timing": {
        "ta": "பயிற்சி நேரம்",
        "en": "Batch Timing"
    },
    "batch_name": {
        "ta": "காலை பயிற்சி (Morning Batch)",
        "en": "Morning Batch"
    },
    "window_open": {
        "ta": "🟢 வருகை பதிவு நேரம் இயங்குகிறது",
        "en": "🟢 Morning Batch Window OPEN"
    },
    "window_closed": {
        "ta": "🔒 வருகை பதிவு நேரம் முடிவடைந்தது",
        "en": "🔒 Morning Batch Window CLOSED"
    },
    "admin_override_active": {
        "ta": "👑 தலைமை ஆசிரியர் சிறப்பு அனுமதி (Admin Override Active)",
        "en": "👑 Admin Override Active"
    },

    # Dashboard Metrics
    "total_active_students": {
        "ta": "பயிற்சி பெறும் மாணவர்கள்",
        "en": "Total Active Students"
    },
    "present_today": {
        "ta": "இன்று வருகை",
        "en": "Present Today"
    },
    "absent_today": {
        "ta": "இன்று விடுப்பு",
        "en": "Absent Today"
    },
    "not_marked_today": {
        "ta": "பதிவு செய்யப்படாதவை",
        "en": "Not Marked Today"
    },
    "today_overview": {
        "ta": "இன்றைய வருகை விவரம்",
        "en": "Today's Attendance Overview"
    },

    # Attendance Marking
    "select_date": {
        "ta": "தேதியைத் தேர்ந்தெடுக்கவும்",
        "en": "Select Date"
    },
    "mark_all_present": {
        "ta": "✅ அனைவரும் வருகை",
        "en": "✅ Mark All Present"
    },
    "mark_all_absent": {
        "ta": "❌ அனைவரும் விடுப்பு",
        "en": "❌ Mark All Absent"
    },
    "present": {
        "ta": "வருகை",
        "en": "Present"
    },
    "absent": {
        "ta": "விடுப்பு",
        "en": "Absent"
    },
    "not_marked": {
        "ta": "பதிவாகவில்லை",
        "en": "Not Marked"
    },
    "status": {
        "ta": "நிலை",
        "en": "Status"
    },
    "marked_by": {
        "ta": "பதிவு செய்தவர்",
        "en": "Marked By"
    },
    "student_roster": {
        "ta": "மாணவர்கள் பட்டியல்",
        "en": "Student Roster"
    },

    # WhatsApp Alerts
    "whatsapp_send_alert": {
        "ta": "📱 பெற்றோருக்கு வாட்ஸ்அப்",
        "en": "📱 WhatsApp Parent"
    },
    "whatsapp_absentees_banner": {
        "ta": "📱 இன்று விடுப்பு எடுத்த மாணவர்கள் ({count}): பெற்றோருக்கு தகவல் அனுப்பவும்",
        "en": "📱 Absent Students Today ({count}): Send WhatsApp Alerts to Parents"
    },
    "whatsapp_copy_group_msg": {
        "ta": "📋 வாட்ஸ்அப் குழுவிற்கான செய்தியை நகலெடு (Copy Group Notice)",
        "en": "📋 Copy WhatsApp Group Absence Notice"
    },

    # Monthly Register
    "monthly_register_title": {
        "ta": "📑 மாதாந்திர வருகை பதிவேடு (Monthly Attendance Register)",
        "en": "📑 Monthly Attendance Register"
    },
    "select_month": {
        "ta": "மாதம் & ஆண்டைத் தேர்ந்தெடுக்கவும்",
        "en": "Select Month & Year"
    },
    "download_excel": {
        "ta": "📥 எக்செல் பதிவேடு (.xlsx) பதிவிறக்கம்",
        "en": "📥 Download Excel Register (.xlsx)"
    },
    "download_csv": {
        "ta": "📥 சிஎஸ்வி (.csv) பதிவிறக்கம்",
        "en": "📥 Download CSV Register (.csv)"
    },
    "no_attendance_for_month": {
        "ta": "தேர்ந்தெடுக்கப்பட்ட மாதத்தில் வருகை விவரங்கள் எதுவும் இல்லை.",
        "en": "No attendance records found for selected month."
    },

    # Student Management
    "add_new_student": {
        "ta": "புதிய மாணவர் சேர்க்கை (Manual)",
        "en": "Add New Student (Manual)"
    },
    "bulk_upload_tab": {
        "ta": "📁 எக்செல் / சிஎஸ்வி பதிவேற்றம் (Bulk Upload)",
        "en": "📁 Excel / CSV Bulk Upload"
    },
    "manage_students_tab": {
        "ta": "📋 மாணவர்கள் பட்டியல் & நீக்குதல்",
        "en": "📋 Active Students & Delete"
    },
    "reg_no": {
        "ta": "பதிவு எண் (Reg No)",
        "en": "Registration No"
    },
    "student_name": {
        "ta": "மாணவர் பெயர் (Full Name)",
        "en": "Student Name"
    },
    "category": {
        "ta": "பிரிவு (Category)",
        "en": "Category"
    },
    "gender": {
        "ta": "பாலினம் (Gender)",
        "en": "Gender"
    },
    "phone": {
        "ta": "பெற்றோர் அலைபேசி எண் (Phone)",
        "en": "Contact Phone"
    },
    "batch": {
        "ta": "பயிற்சி நேரம் (Batch)",
        "en": "Training Batch"
    },
    "register_student_btn": {
        "ta": "➕ மாணவரைச் சேர்க்கவும்",
        "en": "➕ Register Student"
    },
    "clear_db_title": {
        "ta": "🚨 அனைத்து மாணவர்களையும் நீக்கு (Clear Database)",
        "en": "🚨 Wipe All Students (Clear Database)"
    },
    "clear_db_btn": {
        "ta": "🚨 அனைத்தையும் நீக்கு (Confirm Wipe)",
        "en": "🚨 Wipe All Students and Records"
    },
    "clear_db_confirm": {
        "ta": "ஆம், அனைத்து மாணவர் மற்றும் வருகை பதிவுகளையும் முழுமையாக நீக்க விரும்புகிறேன்.",
        "en": "Yes, permanently wipe all student and attendance records."
    }
}

def t(key: str, lang: str = "ta") -> str:
    """Retrieve translated string for key in specified language."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))

def format_whatsapp_phone(phone_str: str) -> str:
    """Formats phone number into international format for WhatsApp (defaults to 91 for India)."""
    if not phone_str:
        return ""
    digits = "".join([c for c in str(phone_str) if c.isdigit()])
    if len(digits) == 10:
        return f"91{digits}"
    elif len(digits) == 12 and digits.startswith("91"):
        return digits
    elif len(digits) > 10:
        return digits
    return digits

def generate_whatsapp_link(phone: str, student_name: str, attendance_date: str, lang: str = "ta") -> str:
    """Generate 1-click WhatsApp wa.me link for absent student's parent."""
    clean_phone = format_whatsapp_phone(phone)
    if not clean_phone:
        return ""

    if lang == "ta":
        msg = (
            f"வணக்கம்! 🙏\n"
            f"கலைத்தாய் சிலம்பம், குரும்பட்டி பயிற்சியில் இன்று ({attendance_date}) "
            f"உங்கள் பிள்ளை *{student_name}* பங்குபெறவில்லை (விடுப்பு).\n\n"
            f"தொடர்ந்து தவறாமல் சிலம்ப பயிற்சிக்கு அனுப்பி வைக்குமாறு அன்புடன் கேட்டுக்கொள்கிறோம்.\n\n"
            f"- கலைத்தாய் சிலம்பம், குரும்பட்டி 🥋"
        )
    else:
        msg = (
            f"Vanakkam! 🙏\n"
            f"This is from Kalaithai Silambam, Kurumpatti. "
            f"Your ward *{student_name}* was ABSENT for Silambam practice on {attendance_date}.\n\n"
            f"Kindly ensure regular practice attendance.\n\n"
            f"- Kalaithai Silambam, Kurumpatti 🥋"
        )

    encoded = urllib.parse.quote(msg)
    return f"https://wa.me/{clean_phone}?text={encoded}"
