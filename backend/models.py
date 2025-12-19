from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=True, index=True)  # Link to main app user
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    face_encoding = Column(LargeBinary, nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Integer, default=1)  # Soft delete flag
    
    # Relationship
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employee(id={self.id}, name='{self.name}', email='{self.email}')>"

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True)
    employee_name = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)  # Legacy/backward compat
    check_in = Column(DateTime, nullable=True, index=True)
    check_out = Column(DateTime, nullable=True)
    check_in_image = Column(String(500))
    check_out_image = Column(String(500))
    image_path = Column(String(500))  # Legacy
    confidence = Column(Float)
    check_out_confidence = Column(Float, nullable=True)
    
    # Relationship
    employee = relationship("Employee", back_populates="attendance_records")
    
    # Composite index for common queries
    __table_args__ = (
        Index('idx_employee_date', 'employee_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Attendance(id={self.id}, employee='{self.employee_name}', check_in='{self.check_in}', check_out='{self.check_out}')>"
