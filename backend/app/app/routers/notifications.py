from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationResponse
from ..utils.deps import get_current_user, admin_only
from typing import List

router = APIRouter(prefix="/notifications", tags=["Notifications"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[NotificationResponse])
def get_my_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get all notifications for the current user"""
    notifications = db.query(Notification).filter(
        Notification.user_id == user.get("id")
    ).order_by(Notification.created_at.desc()).all()
    return notifications

@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get count of unread notifications"""
    count = db.query(Notification).filter(
        Notification.user_id == user.get("id"),
        Notification.read == False
    ).count()
    return {"count": count}

@router.put("/{notification_id}/read")
def mark_as_read(notification_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.get("id")
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.query(Notification).filter(Notification.id == notification_id).update({"read": True})
    db.commit()
    return {"message": "Notification marked as read"}

@router.put("/mark-all-read")
def mark_all_as_read(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Mark all notifications as read"""
    db.query(Notification).filter(
        Notification.user_id == user.get("id"),
        Notification.read == False
    ).update({"read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
def delete_notification(notification_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Delete a notification"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user.get("id")
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notification)
    db.commit()
    return {"message": "Notification deleted"}

@router.post("/", response_model=NotificationResponse)
def create_notification(
    notification: NotificationCreate, 
    db: Session = Depends(get_db), 
    user=Depends(admin_only)
):
    """Create a notification (admin only)"""
    new_notification = Notification(**notification.dict())
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification
