# FILE: server/src/api/models.py
from sqlalchemy import Column, Integer, String
from .db import Base # <-- Correct relative import

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String) # This will store the HASHED password