# FILE: server/src/api/schemas.py
from pydantic import BaseModel, EmailStr

# Schema for creating a user (expects a password)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Schema for reading a user (never includes the password)
class User(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models

# Schema for the login response token
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for data inside the token
class TokenData(BaseModel):
    email: str | None = None