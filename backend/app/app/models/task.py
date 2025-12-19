from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(String)
    status = Column(String, default="Pending")
    deadline = Column(Date)
    assigned_to = Column(Integer, ForeignKey("users.id"))
