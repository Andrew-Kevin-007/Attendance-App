from pydantic import BaseModel
from datetime import date

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    deadline: date
    assigned_to: int

class TaskUpdate(BaseModel):
    status: str
