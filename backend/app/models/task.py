from sqlalchemy import Column, Integer, String, Date, Text, DateTime, ForeignKey
from datetime import datetime
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    status = Column(String, default="pending")
    deadline = Column(Date)
    assigned_to = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text, nullable=True)  # Employee notes/results
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
