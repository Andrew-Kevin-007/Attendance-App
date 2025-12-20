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
# Note: When using allow_origins=["*"], allow_credentials must be False
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins is "*"
    allow_methods=["*"],
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
