from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
from datetime import datetime, date
import os
import logging
from database import Session, engine, Base
from models import Employee, Attendance
from face_utils import get_face_encoding, compare_faces, encoding_to_bytes, bytes_to_encoding
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {e}")
    raise

# Create uploads directory
UPLOAD_DIR = Config.UPLOAD_DIR
os.makedirs(UPLOAD_DIR, exist_ok=True)
logger.info(f"Upload directory: {os.path.abspath(UPLOAD_DIR)}")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    session = Session()
    try:
        employee_count = session.query(Employee).count()
        attendance_count = session.query(Attendance).count()
        return jsonify({
            "status": "healthy",
            "message": "Face Attendance API is running",
            "database": "connected",
            "employees": employee_count,
            "attendance_records": attendance_count,
            "version": "1.0.0"
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500
    finally:
        session.close()

@app.route('/api/register-face', methods=['POST'])
def register_face():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        image_base64 = data.get('image')
        
        # Validation
        if not all([name, email, image_base64]):
            return jsonify({"error": "Missing required fields: name, email, image"}), 400
        
        if len(name) < 2 or len(name) > 100:
            return jsonify({"error": "Name must be between 2 and 100 characters"}), 400
            
        if '@' not in email or len(email) > 255:
            return jsonify({"error": "Invalid email format"}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return jsonify({"error": "Failed to decode image"}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {str(e)}"}), 400
        
        # Get face encoding with quality checks
        result = get_face_encoding(frame)
        if result is None:
            return jsonify({"error": "No face detected"}), 400
        
        encoding, quality_issues = result
        if quality_issues:
            return jsonify({"error": "Face quality issues", "issues": quality_issues}), 400
        
        # Check if email already exists
        session = Session()
        try:
            existing = session.query(Employee).filter_by(email=email).first()
            if existing:
                return jsonify({"error": "Email already registered"}), 409
            
            # Save employee
            employee = Employee(
                name=name,
                email=email,
                face_encoding=encoding_to_bytes(encoding)
            )
            session.add(employee)
            session.commit()
            session.refresh(employee)
            
            logger.info(f"Employee registered: {employee.name} (ID: {employee.id})")
            
            return jsonify({
                "success": True,
                "message": "Face registered successfully",
                "employee_id": employee.id,
                "name": employee.name,
                "email": employee.email,
                "registered_at": employee.registered_at.isoformat()
            }), 201
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/mark-attendance', methods=['POST'])
def mark_attendance():
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({"error": "Missing image"}), 400
        
        # Decode base64 image
        try:
            image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None:
                return jsonify({"error": "Failed to decode image"}), 400
        except Exception as e:
            return jsonify({"error": f"Invalid image format: {str(e)}"}), 400
        
        # Get face encoding
        result = get_face_encoding(frame)
        if result is None:
            return jsonify({"error": "No face detected"}), 400
        
        encoding, quality_issues = result
        if quality_issues:
            return jsonify({"error": "Face quality issues", "issues": quality_issues}), 400
        
        # Compare with all registered employees
        session = Session()
        try:
            employees = session.query(Employee).all()
            if not employees:
                return jsonify({"error": "No employees registered"}), 404
            
            best_match = None
            best_confidence = 0
            
            for employee in employees:
                stored_encoding = bytes_to_encoding(employee.face_encoding)
                is_match, confidence = compare_faces(stored_encoding, encoding)
                
                if is_match and confidence > best_confidence:
                    best_match = employee
                    best_confidence = confidence
            
            if not best_match:
                return jsonify({"error": "Face not recognized"}), 404
            
            # Check if already marked attendance today
            today = date.today()
            existing_attendance = session.query(Attendance).filter(
                Attendance.employee_id == best_match.id,
                Attendance.timestamp >= datetime.combine(today, datetime.min.time())
            ).first()
            
            if existing_attendance:
                return jsonify({
                    "message": "Attendance already marked today",
                    "employee_name": best_match.name,
                    "marked_at": existing_attendance.timestamp.isoformat()
                }), 200
            
            # Save image
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{best_match.id}_{timestamp_str}.jpg"
            image_path = os.path.join(UPLOAD_DIR, image_filename)
            cv2.imwrite(image_path, frame)
            
            # Mark attendance
            attendance = Attendance(
                employee_id=best_match.id,
                employee_name=best_match.name,
                image_path=image_path,
                confidence=best_confidence
            )
            session.add(attendance)
            session.commit()
            
            return jsonify({
                "message": "Attendance marked successfully",
                "employee_id": best_match.id,
                "employee_name": best_match.name,
                "confidence": round(best_confidence, 2),
                "timestamp": attendance.timestamp.isoformat()
            }), 201
        finally:
            session.close()
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        session = Session()
        try:
            employees = session.query(Employee).all()
            return jsonify([{
                "id": emp.id,
                "name": emp.name,
                "email": emp.email,
                "registered_at": emp.registered_at.isoformat()
            } for emp in employees]), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance/<int:employee_id>', methods=['GET'])
def get_attendance_by_employee(employee_id):
    try:
        session = Session()
        try:
            attendance_records = session.query(Attendance).filter_by(employee_id=employee_id).all()
            return jsonify([{
                "id": record.id,
                "employee_name": record.employee_name,
                "timestamp": record.timestamp.isoformat(),
                "confidence": record.confidence
            } for record in attendance_records]), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/attendance', methods=['GET'])
def get_all_attendance():
    try:
        session = Session()
        try:
            attendance_records = session.query(Attendance).all()
            return jsonify([{
                "id": record.id,
                "employee_id": record.employee_id,
                "employee_name": record.employee_name,
                "timestamp": record.timestamp.isoformat(),
                "confidence": record.confidence
            } for record in attendance_records]), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        session = Session()
        try:
            employee = session.query(Employee).filter_by(id=employee_id).first()
            if not employee:
                return jsonify({"error": "Employee not found"}), 404
            
            # Delete attendance records
            session.query(Attendance).filter_by(employee_id=employee_id).delete()
            session.delete(employee)
            session.commit()
            
            return jsonify({"message": "Employee deleted successfully"}), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
