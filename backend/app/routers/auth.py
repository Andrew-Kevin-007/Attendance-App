from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.auth import hash_password, verify_password, create_access_token
from ..utils.deps import admin_only, get_current_user
from ..utils.email import send_password_reset_email
from datetime import datetime, timedelta
import secrets
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

# Frontend URL for password reset
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(user.password)
    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created"}

@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email, "role": user.role, "name": user.name, "id": user.id})
    return {"access_token": token, "token_type": "bearer", "user": {"name": user.name, "email": user.email, "role": user.role}}

@router.get("/users")
def get_users(db: Session = Depends(get_db), user=Depends(admin_only)):
    users = db.query(User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role} for u in users]

@router.get("/me")
def get_me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    user_obj = db.query(User).filter(User.email == user.get("sub")).first()
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_obj.id, "name": user_obj.name, "email": user_obj.email, "role": user_obj.role}

@router.post("/add-employee")
def add_employee(user_data: UserCreate, db: Session = Depends(get_db), current_user=Depends(admin_only)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hashed,
        role=user_data.role if user_data.role else "employee"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Employee added successfully", "user": {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}}


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Request a password reset. Sends an email with a reset link if the email exists.
    Always returns success to prevent email enumeration.
    """
    user = db.query(User).filter(User.email == request.email).first()
    
    if user:
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set token expiry to 1 hour from now
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send reset email
        reset_url = f"{FRONTEND_URL}/reset-password"
        send_password_reset_email(
            to_email=user.email,
            reset_token=reset_token,
            reset_url=reset_url
        )
    
    # Always return success to prevent email enumeration
    return {"message": "If an account with that email exists, a password reset link has been sent."}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Reset password using a valid reset token.
    """
    if not request.token:
        raise HTTPException(status_code=400, detail="Reset token is required")
    
    if not request.new_password or len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    
    # Find user with this token
    user = db.query(User).filter(User.reset_token == request.token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    
    # Check if token has expired
    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        # Clear expired token
        user.reset_token = None
        user.reset_token_expires = None
        db.commit()
        raise HTTPException(status_code=400, detail="Reset token has expired. Please request a new one.")
    
    # Update password
    user.password = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    db.commit()
    
    return {"message": "Password has been reset successfully. You can now log in with your new password."}


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Change password for the currently logged in user.
    Requires the current password for verification.
    """
    user = db.query(User).filter(User.email == current_user.get("sub")).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(request.current_password, user.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Validate new password
    if len(request.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters")
    
    if request.current_password == request.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")
    
    # Update password
    user.password = hash_password(request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

