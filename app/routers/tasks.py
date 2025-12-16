from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from app.utils.deps import admin_only, get_current_user

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
    return {"message": "Task created"}

@router.get("/")
def get_tasks(db: Session = Depends(get_db)):
    return db.query(Task).all()

@router.put("/{task_id}")
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id).first()
    task.status = data.status
    db.commit()
    return {"message": "Task updated"}
