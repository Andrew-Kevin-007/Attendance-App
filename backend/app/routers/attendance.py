from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import base64
import os
import sys
import numpy as np

from ..utils.deps import get_current_user, admin_or_manager
from ..database import SessionLocal as MainSession
from ..models.user import User

# Import face recognition modules from backend root
import sys
import os
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from database import Session as FaceSession  # type: ignore
from models import Employee, Attendance  # type: ignore
from face_utils import get_face_encoding, compare_faces, encoding_to_bytes, bytes_to_encoding  # type: ignore
from config import Config  # type: ignore
import cv2  # type: ignore


router = APIRouter(prefix="/attendance", tags=["attendance"])


class RegisterFaceBody(BaseModel):
    user_id: int
    image: str  # data URL (image/jpeg)


class MarkBody(BaseModel):
    image: str
    action: str = "check_in"  # "check_in" or "check_out"


@router.get("/status-today")
def status_today(user=Depends(get_current_user)):
    face_db = FaceSession()
    try:
        emp = face_db.query(Employee).filter(Employee.user_id == str(user["id"]))
        emp = emp.first()
        registered = emp is not None
        checked_in = False
        checked_out = False
        check_in_time: Optional[str] = None
        check_out_time: Optional[str] = None
        elapsed_seconds: Optional[int] = None
        
        if emp:
            today = date.today()
            rec = (
                face_db.query(Attendance)
                .filter(
                    Attendance.employee_id == emp.id,
                    Attendance.timestamp >= datetime.combine(today, datetime.min.time()),
                )
                .first()
            )
            if rec:
                checked_in = rec.check_in is not None
                checked_out = rec.check_out is not None
                if rec.check_in:
                    check_in_time = rec.check_in.isoformat()
                if rec.check_out:
                    check_out_time = rec.check_out.isoformat()
                    # Calculate elapsed time
                    if rec.check_in and rec.check_out:
                        elapsed_seconds = int((rec.check_out - rec.check_in).total_seconds())
                elif rec.check_in:
                    # Calculate elapsed since check-in
                    elapsed_seconds = int((datetime.now() - rec.check_in).total_seconds())
                    
        return {
            "registered": registered, 
            "markedToday": checked_in,  # backward compat
            "checkedIn": checked_in,
            "checkedOut": checked_out,
            "checkInTime": check_in_time,
            "checkOutTime": check_out_time,
            "elapsedSeconds": elapsed_seconds,
            "timestamp": check_in_time,  # backward compat
        }
    finally:
        face_db.close()


@router.post("/register")
def register_face(body: RegisterFaceBody, _=Depends(admin_or_manager)):
    # Lookup main user
    main_db = MainSession()
    try:
        user_obj: Optional[User] = main_db.query(User).filter(User.id == body.user_id).first()
        if not user_obj:
            raise HTTPException(status_code=404, detail="User not found")
        name = user_obj.name
        email = user_obj.email
    finally:
        main_db.close()

    # Decode image data URL
    try:
        payload = body.image.split(",", 1)[1] if "," in body.image else body.image
        img_bytes = base64.b64decode(payload)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    # Create encoding with quality checks
    result = get_face_encoding(frame)
    if result is None:
        raise HTTPException(status_code=400, detail="No face detected")
    encoding, quality_issues = result
    if quality_issues:
        raise HTTPException(status_code=400, detail={"message": "Face quality issues", "issues": quality_issues})

    face_db = FaceSession()
    try:
        existing = (
            face_db.query(Employee)
            .filter((Employee.user_id == str(body.user_id)) | (Employee.email == email))
            .first()
        )
        if existing:
            existing.name = name
            existing.email = email
            existing.user_id = str(body.user_id)
            existing.face_encoding = encoding_to_bytes(encoding)
            face_db.commit()
            face_db.refresh(existing)
            return {"message": "Face updated for user", "employee_id": existing.id}
        else:
            emp = Employee(
                name=name,
                email=email,
                user_id=str(body.user_id),
                face_encoding=encoding_to_bytes(encoding),
            )
            face_db.add(emp)
            face_db.commit()
            face_db.refresh(emp)
            return {"message": "Face registered", "employee_id": emp.id}
    finally:
        face_db.close()


@router.post("/mark")
def mark_attendance(body: MarkBody, user=Depends(get_current_user)):
    action = body.action.lower()
    if action not in ["check_in", "check_out"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'check_in' or 'check_out'")
    
    # Decode image
    try:
        payload = body.image.split(",", 1)[1] if "," in body.image else body.image
        img_bytes = base64.b64decode(payload)
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Failed to decode image")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    # Encoding
    result = get_face_encoding(frame)
    if result is None:
        raise HTTPException(status_code=400, detail="No face detected")
    encoding, quality_issues = result
    if quality_issues:
        raise HTTPException(status_code=400, detail={"message": "Face quality issues", "issues": quality_issues})

    face_db = FaceSession()
    try:
        employees = face_db.query(Employee).all()
        if not employees:
            raise HTTPException(status_code=404, detail="No employees registered")

        best_match = None
        best_conf = 0.0
        for emp in employees:
            stored = bytes_to_encoding(emp.face_encoding)
            is_match, conf = compare_faces(stored, encoding)
            if is_match and conf > best_conf:
                best_match = emp
                best_conf = conf

        if not best_match:
            raise HTTPException(status_code=404, detail="Face not recognized")

        # Verify recognized identity is the current user
        if best_match.user_id != str(user["id"]):
            raise HTTPException(status_code=403, detail="Face does not match current user")

        # Check for existing record today
        today = date.today()
        existing = (
            face_db.query(Attendance)
            .filter(
                Attendance.employee_id == best_match.id,
                Attendance.timestamp >= datetime.combine(today, datetime.min.time()),
            )
            .first()
        )
        
        # Save image
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{best_match.id}_{action}_{ts}.jpg"
        image_path = os.path.join(Config.UPLOAD_DIR, image_filename)
        cv2.imwrite(image_path, frame)
        
        now = datetime.now()
        
        if action == "check_in":
            if existing and existing.check_in:
                elapsed = None
                if existing.check_out:
                    elapsed = int((existing.check_out - existing.check_in).total_seconds())
                else:
                    elapsed = int((now - existing.check_in).total_seconds())
                return {
                    "message": "Already checked in today",
                    "employee_id": best_match.id,
                    "employee_name": best_match.name,
                    "confidence": round(best_conf, 2),
                    "checkInTime": existing.check_in.isoformat(),
                    "checkOutTime": existing.check_out.isoformat() if existing.check_out else None,
                    "elapsedSeconds": elapsed,
                    "timestamp": existing.check_in.isoformat(),
                }
            
            if existing:
                # Update existing record
                existing.check_in = now
                existing.check_in_image = image_path
                existing.confidence = float(best_conf)
                face_db.commit()
                rec = existing
            else:
                # Create new record
                rec = Attendance(
                    employee_id=best_match.id,
                    employee_name=best_match.name,
                    timestamp=now,
                    check_in=now,
                    check_in_image=image_path,
                    image_path=image_path,
                    confidence=float(best_conf),
                )
                face_db.add(rec)
                face_db.commit()

            return {
                "message": "Checked in successfully",
                "employee_id": best_match.id,
                "employee_name": best_match.name,
                "confidence": round(best_conf, 2),
                "checkInTime": now.isoformat(),
                "checkOutTime": None,
                "elapsedSeconds": 0,
                "timestamp": now.isoformat(),
            }
        
        else:  # check_out
            if not existing or not existing.check_in:
                raise HTTPException(status_code=400, detail="You must check in first before checking out")
            
            if existing.check_out:
                elapsed = int((existing.check_out - existing.check_in).total_seconds())
                return {
                    "message": "Already checked out today",
                    "employee_id": best_match.id,
                    "employee_name": best_match.name,
                    "confidence": round(best_conf, 2),
                    "checkInTime": existing.check_in.isoformat(),
                    "checkOutTime": existing.check_out.isoformat(),
                    "elapsedSeconds": elapsed,
                    "timestamp": existing.check_in.isoformat(),
                }
            
            existing.check_out = now
            existing.check_out_image = image_path
            existing.check_out_confidence = float(best_conf)
            face_db.commit()
            
            elapsed = int((now - existing.check_in).total_seconds())
            
            return {
                "message": "Checked out successfully",
                "employee_id": best_match.id,
                "employee_name": best_match.name,
                "confidence": round(best_conf, 2),
                "checkInTime": existing.check_in.isoformat(),
                "checkOutTime": now.isoformat(),
                "elapsedSeconds": elapsed,
                "timestamp": existing.check_in.isoformat(),
            }
    finally:
        face_db.close()


@router.get("/today-summary")
def today_summary(_=Depends(admin_or_manager)):
    """Return attendance status for all users for today.
    Includes registration status and whether attendance has been marked today.
    """
    main_db = MainSession()
    face_db = FaceSession()
    try:
        users = main_db.query(User).all()
        today = date.today()
        summary = []
        present_count = 0
        registered_count = 0
        checked_out_count = 0

        # Preload all employees and today's attendance into maps for efficiency
        employees = face_db.query(Employee).all()
        by_user_id = {e.user_id: e for e in employees if e.user_id}

        for u in users:
            emp = by_user_id.get(str(u.id))
            registered = emp is not None
            checked_in = False
            checked_out = False
            check_in_time = None
            check_out_time = None
            elapsed_seconds = None
            
            if emp:
                registered_count += 1
                rec = (
                    face_db.query(Attendance)
                    .filter(
                        Attendance.employee_id == emp.id,
                        Attendance.timestamp >= datetime.combine(today, datetime.min.time()),
                    )
                    .first()
                )
                if rec:
                    if rec.check_in:
                        checked_in = True
                        present_count += 1
                        check_in_time = rec.check_in.isoformat()
                    if rec.check_out:
                        checked_out = True
                        checked_out_count += 1
                        check_out_time = rec.check_out.isoformat()
                    # Calculate elapsed
                    if rec.check_in and rec.check_out:
                        elapsed_seconds = int((rec.check_out - rec.check_in).total_seconds())
                    elif rec.check_in:
                        elapsed_seconds = int((datetime.now() - rec.check_in).total_seconds())
                        
            summary.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "registered": registered,
                    "markedToday": checked_in,  # backward compat
                    "checkedIn": checked_in,
                    "checkedOut": checked_out,
                    "checkInTime": check_in_time,
                    "checkOutTime": check_out_time,
                    "elapsedSeconds": elapsed_seconds,
                    "timestamp": check_in_time,  # backward compat
                }
            )

        return {
            "date": today.isoformat(),
            "totals": {
                "users": len(users),
                "registered": registered_count,
                "present": present_count,
                "absent": len(users) - present_count,
                "checkedOut": checked_out_count,
            },
            "items": summary,
        }
    finally:
        main_db.close()
        face_db.close()


@router.get("/users")
def list_users_minimal(_=Depends(admin_or_manager)):
    """List users for selection in face registration (admin/manager)."""
    db = MainSession()
    try:
        users = db.query(User).all()
        return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]
    finally:
        db.close()
