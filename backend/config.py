"""Configuration settings for Face Attendance System"""
import os

class Config:
    """Base configuration"""
    # Database
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///face_attendance.db')
    
    # Upload directory
    UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
    
    # Face recognition settings
    FACE_MIN_SIZE = int(os.getenv('FACE_MIN_SIZE', '50'))
    FACE_SCALE_FACTOR = float(os.getenv('FACE_SCALE_FACTOR', '1.1'))
    FACE_MIN_NEIGHBORS = int(os.getenv('FACE_MIN_NEIGHBORS', '5'))
    
    # Quality thresholds
    BRIGHTNESS_MIN = int(os.getenv('BRIGHTNESS_MIN', '30'))
    BRIGHTNESS_MAX = int(os.getenv('BRIGHTNESS_MAX', '230'))
    BLUR_THRESHOLD = int(os.getenv('BLUR_THRESHOLD', '30'))
    
    # Matching settings
    MATCH_TOLERANCE = float(os.getenv('MATCH_TOLERANCE', '0.4'))
    
    # Server settings
    HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    PORT = int(os.getenv('FLASK_PORT', '5000'))
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # CORS settings
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
