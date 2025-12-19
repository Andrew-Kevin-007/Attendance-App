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

# Ensure we can import face backend modules before any imports
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FACE_BACKEND_PATH = os.path.join(WORKSPACE_ROOT, "face", "backend")
if FACE_BACKEND_PATH not in sys.path:
    sys.path.insert(0, FACE_BACKEND_PATH)

# Now import face backend modules
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


@router.get("/status-today")
def status_today(user=Depends(get_current_user)):
    face_db = FaceSession()
    try:
        emp = face_db.query(Employee).filter(Employee.user_id == str(user["id"]))
        emp = emp.first()
        registered = emp is not None
        marked = False
        marked_at: Optional[str] = None
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
                marked = True
                marked_at = rec.timestamp.isoformat()
        return {"registered": registered, "markedToday": marked, "timestamp": marked_at}
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

        # Check if already marked today
        today = date.today()
        existing = (
            face_db.query(Attendance)
            .filter(
                Attendance.employee_id == best_match.id,
                Attendance.timestamp >= datetime.combine(today, datetime.min.time()),
            )
            .first()
        )
        if existing:
            return {
                "message": "Attendance already marked today",
                "employee_id": best_match.id,
                "employee_name": best_match.name,
                "confidence": round(best_conf, 2),
                "timestamp": existing.timestamp.isoformat(),
            }

        # Save image
        os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{best_match.id}_{ts}.jpg"
        image_path = os.path.join(Config.UPLOAD_DIR, image_filename)
        cv2.imwrite(image_path, frame)

        rec = Attendance(
            employee_id=best_match.id,
            employee_name=best_match.name,
            image_path=image_path,
            confidence=float(best_conf),
        )
        face_db.add(rec)
        face_db.commit()

        return {
            "message": "Attendance marked successfully",
            "employee_id": best_match.id,
            "employee_name": best_match.name,
            "confidence": round(best_conf, 2),
            "timestamp": rec.timestamp.isoformat(),
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

        # Preload all employees and today's attendance into maps for efficiency
        employees = face_db.query(Employee).all()
        by_user_id = {e.user_id: e for e in employees if e.user_id}

        for u in users:
            emp = by_user_id.get(str(u.id))
            registered = emp is not None
            marked = False
            ts = None
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
                    marked = True
                    present_count += 1
                    ts = rec.timestamp.isoformat()
            summary.append(
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "registered": registered,
                    "markedToday": marked,
                    "timestamp": ts,
                }
            )

        return {
            "date": today.isoformat(),
            "totals": {
                "users": len(users),
                "registered": registered_count,
                "present": present_count,
                "absent": len(users) - present_count,
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
