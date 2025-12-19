from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    user_id: int
    title: str
    message: str
    type: Optional[str] = "info"

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    type: str
    read: bool
    created_at: datetime

    class Config:
        from_attributes = True
