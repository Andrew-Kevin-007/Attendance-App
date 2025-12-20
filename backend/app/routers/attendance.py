from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
import base64
import os
import sys
import numpy as np
import csv
import io

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
from models import Employee, Attendance, FaceSample  # type: ignore
from face_utils import get_face_encoding, compare_faces, compare_faces_multi, encoding_to_bytes, bytes_to_encoding  # type: ignore
from config import Config  # type: ignore
import cv2  # type: ignore


router = APIRouter(prefix="/attendance", tags=["attendance"])


class RegisterFaceBody(BaseModel):
    user_id: int
    image: str  # data URL (image/jpeg)
    add_sample: bool = False  # If True, adds additional training sample instead of replacing


class MarkBody(BaseModel):
    image: str
    action: str = "check_in"  # "check_in" or "check_out"


class BulkAttendanceItem(BaseModel):
    user_id: int
    date: str  # YYYY-MM-DD
    check_in: Optional[str] = None  # HH:MM
    check_out: Optional[str] = None  # HH:MM
    status: str = "present"  # present, absent, late


class BulkAttendanceBody(BaseModel):
    records: List[BulkAttendanceItem]


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
        
        # Calculate quality score
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        quality_score = float(cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0)  # Normalize
        
        if existing:
            if body.add_sample:
                # Add as additional training sample
                sample = FaceSample(
                    employee_id=existing.id,
                    face_encoding=encoding_to_bytes(encoding),
                    quality_score=quality_score
                )
                face_db.add(sample)
                face_db.commit()
                
                # Count total samples
                sample_count = face_db.query(FaceSample).filter(
                    FaceSample.employee_id == existing.id
                ).count() + 1  # +1 for primary encoding
                
                return {
                    "message": f"Training sample added ({sample_count} total samples)",
                    "employee_id": existing.id,
                    "sample_count": sample_count
                }
            else:
                # Update primary encoding
                existing.name = name
                existing.email = email
                existing.user_id = str(body.user_id)
                existing.face_encoding = encoding_to_bytes(encoding)
                face_db.commit()
                face_db.refresh(existing)
                return {"message": "Face updated for user", "employee_id": existing.id}
        else:
            # Create new employee with primary encoding
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
        all_matches = []  # For debugging
        
        for emp in employees:
            # Collect all encodings for this employee (primary + samples)
            encodings = [bytes_to_encoding(emp.face_encoding)]
            
            # Add additional training samples
            samples = face_db.query(FaceSample).filter(
                FaceSample.employee_id == emp.id
            ).all()
            for sample in samples:
                encodings.append(bytes_to_encoding(sample.face_encoding))
            
            # Compare against all encodings (uses best match)
            is_match, conf = compare_faces_multi(encodings, encoding, tolerance=0.50)  # 50% confidence
            all_matches.append(f"{emp.name}: {conf:.1%} ({len(encodings)} samples)")
            
            if is_match and conf > best_conf:
                best_match = emp
                best_conf = conf

        if not best_match:
            matches_info = ", ".join(all_matches[:3]) if all_matches else "No faces to compare"
            raise HTTPException(
                status_code=404, 
                detail=f"Face not recognized. Top matches: {matches_info}. Try: 1) Better lighting 2) Face camera directly 3) Register more training samples"
            )

        # Verify recognized identity is the current user
        if best_match.user_id != str(user["id"]):
            raise HTTPException(status_code=403, detail="Face does not match current user")

        # Auto-train: Add successful captures as training samples (with quality threshold)
        # Only add if confidence is good and we don't have too many samples already
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        quality_score = float(cv2.Laplacian(gray, cv2.CV_64F).var() / 1000.0)
        
        sample_count = face_db.query(FaceSample).filter(
            FaceSample.employee_id == best_match.id
        ).count()
        
        # Add to training if: high confidence (>70%), good quality (>50), and <20 samples
        if best_conf > 0.70 and quality_score > 0.05 and sample_count < 20:
            try:
                new_sample = FaceSample(
                    employee_id=best_match.id,
                    face_encoding=encoding_to_bytes(encoding),
                    quality_score=quality_score
                )
                face_db.add(new_sample)
                face_db.commit()
            except Exception:
                # Silently fail - training is optional
                pass

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


@router.get("/export")
def export_attendance(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    format: str = Query("csv", description="Export format: csv or json"),
    _=Depends(admin_or_manager)
):
    """Export attendance records for a date range as CSV or JSON."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # Include end date
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    if start > end:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    main_db = MainSession()
    face_db = FaceSession()
    try:
        # Get all users
        users = main_db.query(User).all()
        user_map = {str(u.id): u for u in users}
        
        # Get employees
        employees = face_db.query(Employee).all()
        emp_user_map = {e.id: user_map.get(e.user_id) for e in employees if e.user_id}
        
        # Get attendance records in date range
        records = (
            face_db.query(Attendance)
            .filter(
                Attendance.timestamp >= start,
                Attendance.timestamp < end
            )
            .order_by(Attendance.timestamp.desc())
            .all()
        )
        
        # Build export data
        export_data = []
        for rec in records:
            user = emp_user_map.get(rec.employee_id)
            
            # Calculate work hours
            work_hours = None
            if rec.check_in and rec.check_out:
                seconds = (rec.check_out - rec.check_in).total_seconds()
                work_hours = round(seconds / 3600, 2)
            
            export_data.append({
                "date": rec.timestamp.strftime("%Y-%m-%d") if rec.timestamp else "",
                "employee_id": rec.employee_id,
                "employee_name": rec.employee_name,
                "email": user.email if user else "",
                "role": user.role if user else "",
                "check_in": rec.check_in.strftime("%Y-%m-%d %H:%M:%S") if rec.check_in else "",
                "check_out": rec.check_out.strftime("%Y-%m-%d %H:%M:%S") if rec.check_out else "",
                "work_hours": work_hours if work_hours else "",
                "check_in_confidence": round(rec.confidence, 2) if rec.confidence else "",
                "check_out_confidence": round(rec.check_out_confidence, 2) if rec.check_out_confidence else "",
            })
        
        if format.lower() == "json":
            return {
                "start_date": start_date,
                "end_date": end_date,
                "total_records": len(export_data),
                "records": export_data
            }
        else:
            # Generate CSV
            output = io.StringIO()
            if export_data:
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
            else:
                output.write("No records found for the specified date range")
            
            output.seek(0)
            filename = f"attendance_report_{start_date}_to_{end_date}.csv"
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
    finally:
        main_db.close()
        face_db.close()


@router.get("/history")
def get_attendance_history(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    _=Depends(admin_or_manager)
):
    """Get attendance history with optional filters."""
    main_db = MainSession()
    face_db = FaceSession()
    try:
        # Default to last 30 days if no dates specified
        if not end_date:
            end = datetime.now() + timedelta(days=1)
        else:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        if not start_date:
            start = end - timedelta(days=30)
        else:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        # Get users
        users = main_db.query(User).all()
        user_map = {str(u.id): u for u in users}
        
        # Build query
        query = face_db.query(Attendance).filter(
            Attendance.timestamp >= start,
            Attendance.timestamp < end
        )
        
        # Filter by user if specified
        if user_id:
            emp = face_db.query(Employee).filter(Employee.user_id == str(user_id)).first()
            if emp:
                query = query.filter(Attendance.employee_id == emp.id)
            else:
                return {"records": [], "total": 0}
        
        records = query.order_by(Attendance.timestamp.desc()).all()
        
        # Get employees for mapping
        employees = face_db.query(Employee).all()
        emp_user_map = {e.id: user_map.get(e.user_id) for e in employees if e.user_id}
        
        result = []
        for rec in records:
            user = emp_user_map.get(rec.employee_id)
            work_hours = None
            if rec.check_in and rec.check_out:
                seconds = (rec.check_out - rec.check_in).total_seconds()
                work_hours = round(seconds / 3600, 2)
            
            result.append({
                "id": rec.id,
                "date": rec.timestamp.strftime("%Y-%m-%d") if rec.timestamp else None,
                "employee_id": rec.employee_id,
                "employee_name": rec.employee_name,
                "email": user.email if user else None,
                "role": user.role if user else None,
                "check_in": rec.check_in.isoformat() if rec.check_in else None,
                "check_out": rec.check_out.isoformat() if rec.check_out else None,
                "work_hours": work_hours,
                "confidence": round(rec.confidence, 2) if rec.confidence else None,
            })
        
        return {
            "start_date": start.strftime("%Y-%m-%d"),
            "end_date": (end - timedelta(days=1)).strftime("%Y-%m-%d"),
            "total": len(result),
            "records": result
        }
    finally:
        main_db.close()
        face_db.close()


@router.post("/bulk")
def bulk_add_attendance(
    body: BulkAttendanceBody,
    _=Depends(admin_or_manager)
):
    """
    Add attendance records in bulk (admin/manager only).
    Useful for importing historical data or marking attendance for multiple users.
    """
    main_db = MainSession()
    face_db = FaceSession()
    try:
        results = {
            "success": [],
            "errors": []
        }
        
        for item in body.records:
            try:
                # Get user
                user = main_db.query(User).filter(User.id == item.user_id).first()
                if not user:
                    results["errors"].append({
                        "user_id": item.user_id,
                        "date": item.date,
                        "error": "User not found"
                    })
                    continue
                
                # Get or check employee
                emp = face_db.query(Employee).filter(Employee.user_id == str(item.user_id)).first()
                if not emp:
                    results["errors"].append({
                        "user_id": item.user_id,
                        "date": item.date,
                        "error": "Employee face not registered"
                    })
                    continue
                
                # Parse date
                try:
                    record_date = datetime.strptime(item.date, "%Y-%m-%d")
                except ValueError:
                    results["errors"].append({
                        "user_id": item.user_id,
                        "date": item.date,
                        "error": "Invalid date format. Use YYYY-MM-DD"
                    })
                    continue
                
                # Parse times
                check_in_dt = None
                check_out_dt = None
                
                if item.check_in:
                    try:
                        time_parts = item.check_in.split(":")
                        check_in_dt = record_date.replace(
                            hour=int(time_parts[0]),
                            minute=int(time_parts[1]) if len(time_parts) > 1 else 0
                        )
                    except (ValueError, IndexError):
                        results["errors"].append({
                            "user_id": item.user_id,
                            "date": item.date,
                            "error": "Invalid check_in time format. Use HH:MM"
                        })
                        continue
                
                if item.check_out:
                    try:
                        time_parts = item.check_out.split(":")
                        check_out_dt = record_date.replace(
                            hour=int(time_parts[0]),
                            minute=int(time_parts[1]) if len(time_parts) > 1 else 0
                        )
                    except (ValueError, IndexError):
                        results["errors"].append({
                            "user_id": item.user_id,
                            "date": item.date,
                            "error": "Invalid check_out time format. Use HH:MM"
                        })
                        continue
                
                # Check for existing record on this date
                existing = (
                    face_db.query(Attendance)
                    .filter(
                        Attendance.employee_id == emp.id,
                        Attendance.timestamp >= record_date,
                        Attendance.timestamp < record_date + timedelta(days=1),
                    )
                    .first()
                )
                
                if existing:
                    # Update existing record
                    if check_in_dt:
                        existing.check_in = check_in_dt
                    if check_out_dt:
                        existing.check_out = check_out_dt
                    face_db.commit()
                    results["success"].append({
                        "user_id": item.user_id,
                        "date": item.date,
                        "action": "updated",
                        "record_id": existing.id
                    })
                else:
                    # Create new record
                    new_rec = Attendance(
                        employee_id=emp.id,
                        employee_name=user.name,
                        timestamp=record_date,
                        check_in=check_in_dt,
                        check_out=check_out_dt,
                        confidence=1.0,  # Manual entry
                    )
                    face_db.add(new_rec)
                    face_db.commit()
                    face_db.refresh(new_rec)
                    results["success"].append({
                        "user_id": item.user_id,
                        "date": item.date,
                        "action": "created",
                        "record_id": new_rec.id
                    })
                    
            except Exception as e:
                results["errors"].append({
                    "user_id": item.user_id,
                    "date": item.date,
                    "error": str(e)
                })
        
        return {
            "message": f"Processed {len(body.records)} records",
            "success_count": len(results["success"]),
            "error_count": len(results["errors"]),
            "results": results
        }
    finally:
        main_db.close()
        face_db.close()


@router.delete("/bulk")
def bulk_delete_attendance(
    record_ids: List[int] = Query(..., description="List of attendance record IDs to delete"),
    _=Depends(admin_or_manager)
):
    """Delete multiple attendance records at once (admin/manager only)."""
    face_db = FaceSession()
    try:
        deleted_count = 0
        not_found = []
        
        for record_id in record_ids:
            record = face_db.query(Attendance).filter(Attendance.id == record_id).first()
            if record:
                face_db.delete(record)
                deleted_count += 1
            else:
                not_found.append(record_id)
        
        face_db.commit()
        
        return {
            "message": f"Deleted {deleted_count} records",
            "deleted_count": deleted_count,
            "not_found": not_found
        }
    finally:
        face_db.close()
