# Attendance Tracker - Setup & Run Guide

## ✅ Setup Complete

Your project is now configured with:
- Python 3.14 virtual environment (`.venv312`)
- All backend dependencies (FastAPI, Flask, OpenCV, NumPy, etc.)
- Face recognition integration
- Admin dashboard with attendance tracking

## 🚀 Running the Application

### Option 1: Quick Start (Windows)

From the project root, run the all-in-one startup script:

```powershell
.\start-all.ps1
```

This will start both backend and frontend in separate terminal windows.

### Option 2: Manual Start

#### Backend (FastAPI + Face Recognition)

From the project root:

```powershell
# Navigate to backend
cd backend

# Activate the virtual environment
python -m venv venv
venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies (first time only)
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set SECRET_KEY

# Run the backend server (or use .\start.ps1)
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

**Note:** Do not use `--reload` flag as it causes OpenCV import issues in subprocess.

Backend will be available at: **http://127.0.0.1:8001**

### Frontend (React + Vite)

In a new terminal:

```powershell
cd frontend
npm install  # First time only
npm run dev
```

Frontend will be available at: **http://localhost:5173**

## 📋 Key Features

### Attendance Flow
1. **Login** → User logs in with credentials
2. **Face Recognition** → Redirected to `/attendance` to mark attendance via webcam
3. **Dashboard** → After successful face recognition, access full app

### Admin/Manager Features
- **Today's Attendance Card** on Dashboard showing:
  - Total users, registered faces, present/absent counts
  - Per-employee status table
- **Register Face** at `/attendance/register`:
  - Select any employee from dropdown
  - Capture face via premium webcam UI
  - Links face to user account

### API Endpoints

#### Attendance
- `GET /attendance/status-today` - Check if current user marked attendance
- `POST /attendance/mark` - Mark attendance with face recognition
- `POST /attendance/register` - Register face (admin/manager only)
- `GET /attendance/today-summary` - Daily attendance report (admin/manager)
- `GET /attendance/users` - List users for registration (admin/manager)

#### Legacy Face Service (mounted)
- `GET /face/api/health` - Face service health check
- Available at `/face/api/*` for backward compatibility

## 🔑 Default Test Users

Create users via the signup page or use the auth API. Role can be: `admin`, `manager`, or `employee`.

## 🎨 UI Highlights

- **Apple-inspired design** with glass morphism and smooth animations
- **Premium webcam capture UI** with circular guide and status overlays
- **Server-side attendance gating** - no localStorage hacks
- **Identity verification** - Face must match logged-in user

## 🐛 Troubleshooting

### Port already in use
If port 8001 is occupied:
```powershell
Get-NetTCPConnection -LocalPort 8001 | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
```

### OpenCV import errors
The project uses opencv-python (not headless). If cv2 import fails:
```powershell
.\.venv312\Scripts\python.exe -m pip install --force-reinstall opencv-python --no-deps
```

### CORS errors
Ensure environment variable is set:
```powershell
setx ALLOWED_ORIGINS "http://localhost:5173,http://127.0.0.1:5173"
```
Then restart the terminal and backend.

## 📁 Project Structure

```
Attendancetracker/
├── .venv312/              # Python virtual environment
├── task-manager/          # FastAPI backend
│   └── app/
│       ├── main.py       # App entry + face service mount
│       ├── routers/
│       │   └── attendance.py  # Attendance endpoints
│       └── ...
├── face/                  # Face recognition module
│   └── backend/
│       ├── app.py        # Flask face service (mounted)
│       ├── face_utils.py # Face detection/encoding
│       └── models.py     # Employee, Attendance models
└── frontend/             # React + Vite
    └── src/
        ├── pages/
        │   ├── Attendance.tsx      # Face capture & mark
        │   ├── RegisterFace.tsx    # Admin face registration
        │   └── Dashboard.tsx       # With attendance card
        └── lib/
            ├── api.ts              # Main API client
            └── attendance.ts       # Attendance API client
```

## 🔄 Development Workflow

1. Make code changes
2. Backend: Restart uvicorn manually (no --reload)
3. Frontend: Hot reload works automatically
4. Test attendance flow with webcam

## 📝 Notes

- Face data stored in `face_attendance.db` (SQLite)
- Main app data in `task.db` (SQLite)
- Employee.user_id links face records to main users
- Uploads saved to `task-manager/uploads/`
