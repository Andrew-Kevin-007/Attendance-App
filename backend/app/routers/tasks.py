from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from app.schemas.task import TaskCreate, TaskUpdate
from ..utils.deps import admin_only, get_current_user
from ..utils.email import send_task_assignment_email, send_task_status_update_email
from datetime import datetime, timedelta

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", dependencies=[Depends(admin_only)])
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority,
        deadline=task.deadline,
        assigned_to=task.assigned_to
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # Send notification to assigned user
    if task.assigned_to:
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        notification = Notification(
            user_id=task.assigned_to,
            title="New Task Assigned",
            message=f"You have been assigned a new task: {task.title}",
            type="info"
        )
        db.add(notification)
        db.commit()
        
        # Send email notification
        if assignee:
            send_task_assignment_email(
                to_email=assignee.email,
                employee_name=assignee.name,
                task_title=task.title,
                task_description=task.description or "",
                deadline=str(task.deadline) if task.deadline else None,
                priority=task.priority or "medium"
            )
    
    return new_task

@router.get("/")
def get_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tasks = db.query(Task).all()
    result = []
    for task in tasks:
        assignee = db.query(User).filter(User.id == task.assigned_to).first()
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "deadline": str(task.deadline),
            "assigned_to": task.assigned_to,
            "assignee_name": assignee.name if assignee else "Unknown"
        })
    return result

@router.get("/my-tasks")
def get_my_tasks(db: Session = Depends(get_db), user=Depends(get_current_user)):
    user_email = user.get("sub")
    user_obj = db.query(User).filter(User.email == user_email).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    
    tasks = db.query(Task).filter(Task.assigned_to == user_obj.id).all()
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "deadline": str(task.deadline)
        })
    return result

@router.put("/{task_id}")
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is assigned to this task or is admin
    user_email = user.get("sub")
    user_obj = db.query(User).filter(User.email == user_email).first()
    is_admin = user.get("role") == "admin"
    
    if not is_admin and task.assigned_to != user_obj.id:
        raise HTTPException(status_code=403, detail="You can only update tasks assigned to you")
    
    # Store old status for email notification
    old_status = task.status
    
    # Build update dict with provided fields
    update_data = {}
    if data.status is not None:
        update_data["status"] = data.status
    if data.notes is not None:
        update_data["notes"] = data.notes
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        db.query(Task).filter(Task.id == task_id).update(update_data)
        db.commit()
        db.refresh(task)
        
        # Send email notification for status change
        if data.status is not None and data.status != old_status:
            assignee = db.query(User).filter(User.id == task.assigned_to).first()
            if assignee:
                send_task_status_update_email(
                    to_email=assignee.email,
                    employee_name=assignee.name,
                    task_title=task.title,
                    old_status=old_status or "pending",
                    new_status=data.status
                )
    
    assignee = db.query(User).filter(User.id == task.assigned_to).first()
    
    return {
        "message": "Task updated",
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "status": task.status,
            "deadline": str(task.deadline),
            "notes": task.notes,
            "updated_at": str(task.updated_at) if task.updated_at else None,
            "assigned_to": task.assigned_to,
            "assignee_name": assignee.name if assignee else "Unknown"
        }
    }


@router.get("/{task_id}")
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get a single task by ID"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Check if user is assigned to this task, is admin, or is manager
    user_email = user.get("sub")
    user_obj = db.query(User).filter(User.email == user_email).first()
    user_role = user.get("role")
    
    if user_role not in ("admin", "manager") and task.assigned_to != user_obj.id:
        raise HTTPException(status_code=403, detail="You can only view tasks assigned to you")
    
    assignee = db.query(User).filter(User.id == task.assigned_to).first()
    
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "deadline": str(task.deadline),
        "notes": task.notes,
        "updated_at": str(task.updated_at) if task.updated_at else None,
        "assigned_to": task.assigned_to,
        "assignee_name": assignee.name if assignee else "Unknown"
    }


@router.get("/stats")
def get_task_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get task statistics for dashboard"""
    # Total counts by status
    total_tasks = db.query(Task).count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    in_progress = db.query(Task).filter(Task.status == "in_progress").count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    
    # Priority distribution
    high_priority = db.query(Task).filter(Task.priority == "high").count()
    medium_priority = db.query(Task).filter(Task.priority == "medium").count()
    low_priority = db.query(Task).filter(Task.priority == "low").count()
    
    # Overdue tasks (deadline passed and not completed)
    today = datetime.now().date()
    overdue = db.query(Task).filter(
        Task.deadline < today,
        Task.status != "completed"
    ).count()
    
    # Team performance - tasks per user
    team_stats = []
    users = db.query(User).all()
    for u in users:
        user_tasks = db.query(Task).filter(Task.assigned_to == u.id).count()
        user_completed = db.query(Task).filter(
            Task.assigned_to == u.id,
            Task.status == "completed"
        ).count()
        if user_tasks > 0:
            team_stats.append({
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "role": u.role,
                "total_tasks": user_tasks,
                "completed": user_completed,
                "completion_rate": round((user_completed / user_tasks) * 100) if user_tasks > 0 else 0
            })
    
    # Recent tasks (last 5)
    recent = db.query(Task).order_by(Task.id.desc()).limit(5).all()
    recent_tasks = []
    for t in recent:
        assignee = db.query(User).filter(User.id == t.assigned_to).first()
        recent_tasks.append({
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "priority": t.priority,
            "deadline": str(t.deadline) if t.deadline else None,
            "assignee_name": assignee.name if assignee else "Unassigned"
        })
    
    # Weekly trend (last 7 days) - tasks created per day
    weekly_trend = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        # For simplicity, we'll just distribute existing tasks
        # In a real app, you'd have created_at timestamps
        day_name = day.strftime("%a")
        weekly_trend.append({
            "day": day_name,
            "date": str(day),
            "completed": 0,
            "created": 0
        })
    
    return {
        "total": total_tasks,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "overdue": overdue,
        "completion_rate": round((completed / total_tasks) * 100) if total_tasks > 0 else 0,
        "priority_distribution": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority
        },
        "status_distribution": {
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending
        },
        "team_performance": team_stats,
        "recent_tasks": recent_tasks,
        "weekly_trend": weekly_trend
    }


@router.delete("/{task_id}", dependencies=[Depends(admin_only)])
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Delete a task (admin only)"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
