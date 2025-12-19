# Attendance Tracker Backend

FastAPI + Flask microservice for task management and face recognition attendance.

## Structure

```text
backend/
├── app/                    # FastAPI application
│   ├── main.py            # Application entry
│   ├── database.py        # Database configuration
│   ├── attendance_mount.py # Flask app mounter
│   ├── models/            # SQLAlchemy models
│   ├── routers/           # API endpoints
│   │   ├── auth.py       # Authentication
│   │   ├── tasks.py      # Task management
│   │   ├── notifications.py
│   │   └── attendance.py # Face attendance
│   └── utils/            # Helpers & dependencies
├── flask_app.py          # Flask face service
├── face_utils.py         # Face recognition logic
├── models.py             # Face data models
├── database.py           # Face DB config
├── config.py             # Settings
└── requirements.txt
```

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set SECRET_KEY

# Run server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## API Endpoints

- `/` - Health check
- `/auth/*` - Authentication
- `/tasks/*` - Task management
- `/notifications/*` - Notifications
- `/attendance/*` - Face attendance
- `/face/api/*` - Legacy face service

## Environment Variables

See `.env.example` for required configuration.
