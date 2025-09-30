# src/api/auth.py (Corrected Code)
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# FIX 1: Changed 'get_connection' to 'get_db'
from src.api.db import get_db 
from src.api.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# Schemas
class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Signup endpoint
# FIX 2: Changed Depends(get_connection) to Depends(get_db)
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # NOTE: Ensure User model has a 'name' field and the password field is 'password' 
    # (or 'hashed_password' if you rename the column in models.py)
    hashed_password = pwd_context.hash(data.password)
    new_user = User(name=data.name, email=data.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.id, "name": new_user.name}

# Login endpoint
# FIX 3: Changed Depends(get_connection) to Depends(get_db)
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    
    # NOTE: Assuming the password column in User model is named 'password'
    if not user or not pwd_context.verify(data.password, user.password): 
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    # NOTE: You will likely want to return a JWT/access token here instead of just user info
    return {"user_id": user.id, "name": user.name}