"""
Verification Test for:
1. WhatsApp Absent Alerts (Tamil & English)
2. Monthly Attendance Grid & Excel Export
3. Bilingual Translations
4. Student Bulk Import & Clear Database
"""

import database
from translations import t, generate_whatsapp_link, format_whatsapp_phone
import pandas as pd
from datetime import date

def run_tests():
    print("[*] Running Verification Tests for New Features...")

    # 1. Clear database test
    database.clear_all_students()
    assert len(database.get_all_students()) == 0, "Database should be clear"
    print("[PASS] 1. Database cleared to 0 students.")

    # 2. Add student & Mark attendance
    ok, msg = database.add_student("101", "Arun Kumar", "Junior", "Male", "9876543210")
    assert ok, msg
    assert len(database.get_all_students()) == 1
    print("[PASS] 2. Student added successfully.")

    today_str = str(date.today())
    database.mark_attendance(database.get_all_students()[0]["id"], today_str, "Absent", "trainer")
    att = database.get_attendance_by_date(today_str)
    assert len(att) == 1
    assert att[0]["status"] == "Absent"
    print("[PASS] 3. Attendance marked as Absent.")

    # 3. WhatsApp 1-Click Link Generation (Tamil & English)
    wa_link_ta = generate_whatsapp_link("9876543210", "Arun Kumar", today_str, "ta")
    assert "https://wa.me/919876543210" in wa_link_ta
    assert "text=" in wa_link_ta
    print("[PASS] 4. Tamil WhatsApp link verified:", wa_link_ta[:60] + "...")

    wa_link_en = generate_whatsapp_link("9876543210", "Arun Kumar", today_str, "en")
    assert "https://wa.me/919876543210" in wa_link_en
    print("[PASS] 5. English WhatsApp link verified:", wa_link_en[:60] + "...")

    # 4. Monthly Register Grid & Excel Generation
    current_ym = date.today().strftime("%Y-%m")
    grid_df, day_cols = database.get_monthly_register_grid(current_ym)
    assert not grid_df.empty, "Grid DF should not be empty"
    assert "Reg No" in grid_df.columns
    assert "Student Name" in grid_df.columns
    assert "Present" in grid_df.columns
    assert "Absent" in grid_df.columns
    print(f"[PASS] 6. Monthly Register Grid verified ({len(day_cols)} days detected).")

    excel_bytes = database.generate_monthly_excel(grid_df, current_ym, "Morning Batch")
    assert len(excel_bytes) > 1000, "Excel bytes should be generated"
    print(f"[PASS] 7. Monthly Excel Workbook generated ({len(excel_bytes)} bytes).")

    # 5. Bulk Student Import
    import_sample = pd.DataFrame([
        {"Reg No": "102", "Student Name": "Kaviya Sri", "Category": "Sub-Junior", "Gender": "Female", "Phone": "9876543211", "Batch": "Morning (06:30 AM - 08:30 AM)"},
        {"Reg No": "103", "Student Name": "Dhanush S", "Category": "Super Senior", "Gender": "Male", "Phone": "9876543212", "Batch": "Morning (06:30 AM - 08:30 AM)"}
    ])
    b_ok, b_cnt, b_msg = database.bulk_import_students(import_sample)
    assert b_ok, b_msg
    assert b_cnt == 2
    assert len(database.get_all_students()) == 3
    print(f"[PASS] 8. Bulk Import verified: {b_cnt} students imported.")

    # 6. Bilingual Translations check
    assert t("nav_dashboard", "ta") == "📊 முகப்பு பலகை"
    assert t("nav_dashboard", "en") == "📊 Dashboard"
    assert t("mark_all_present", "ta") == "✅ அனைவரும் வருகை"
    print("[PASS] 9. Bilingual translations verified.")

    # 7. Final Clean: Leave database completely fresh with 0 students
    database.clear_all_students()
    assert len(database.get_all_students()) == 0
    print("[PASS] 10. Database cleared clean and ready for real student entry.")

    print("\n[SUCCESS] ALL FEATURES VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
