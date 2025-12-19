from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.wsgi import WSGIMiddleware
from .database import engine, Base
from .models import user, task
from .routers import auth, tasks, notifications
from .routers import attendance as attendance_router
import os
from dotenv import load_dotenv
from .attendance_mount import get_flask_app

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Attendance Tracker API",
    description="Task Management & Face Recognition Attendance System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS Configuration - Must be before routers
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:8080,http://localhost:8081,http://127.0.0.1:5173,http://127.0.0.1:5174,http://127.0.0.1:5175")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Attendance Tracker API",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "services": ["auth", "tasks", "notifications", "attendance", "face-recognition"]
    }

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(notifications.router)
app.include_router(attendance_router.router)

# Mount the Face Attendance Flask app under /face
try:
    flask_app = get_flask_app()
    app.mount("/face", WSGIMiddleware(flask_app))
except Exception as e:
    # Do not crash the main app if face service fails to load; log instead
    import logging
    logging.getLogger(__name__).error(f"Failed to mount face attendance service: {e}")
