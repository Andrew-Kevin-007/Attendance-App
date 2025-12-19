from pydantic import BaseModel
from datetime import date
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    description: str
    priority: str
    deadline: date
    assigned_to: int

class TaskUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None
