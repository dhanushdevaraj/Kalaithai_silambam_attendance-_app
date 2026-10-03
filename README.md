# Kalaithai Silambam - Kurumpatti Attendance System

## Features
- **Morning Batch Schedule**: Fixed batch timing **6:30 AM to 8:30 AM (Morning Only)**
- **Attendance Time Window Lock**: Trainers can only mark attendance during the 6:30 AM – 8:30 AM window
- **Admin Override Mode**: Master Admin can mark and modify attendance anytime (24/7 override)
- Role-based Access (Admin & Trainer)
- Student directory with batch assignment
- Mark Present/Absent & Mark All Present/Absent
- Attendance history & filtered dates
- Individual attendance reports with percentage tracking
- SQLite database with automatic migrations
- Glassmorphic dark UI with batch status badges

## Default login
Username: admin
Password: admin123

Change the default password before real-world use.

## Windows setup
```powershell
python -m venv venv
.\venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501
