from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin
from app.utils.auth import hash_password, verify_password, create_access_token
from ..utils.deps import admin_only, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
