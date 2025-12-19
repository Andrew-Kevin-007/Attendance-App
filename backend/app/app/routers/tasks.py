from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.task import Task
from app.models.user import User
from app.models.notification import Notification
from app.schemas.task import TaskCreate, TaskUpdate
from ..utils.deps import admin_only, get_current_user

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
        notification = Notification(
            user_id=task.assigned_to,
            title="New Task Assigned",
            message=f"You have been assigned a new task: {task.title}",
            type="info"
        )
        db.add(notification)
        db.commit()
    
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
    
    # Update status
    db.query(Task).filter(Task.id == task_id).update({"status": data.status})
    db.commit()
    db.refresh(task)
    
    return {"message": "Task updated", "task": {"id": task.id, "status": task.status}}
