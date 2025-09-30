# src/api/models.py (Updated)

from sqlalchemy import Column, Integer, String
from .db import Base 

class User(Base):
    __tablename__ = "users"
    
    # FIX: Add __table_args__ to allow redefinition during reload/multiple imports
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    # Storing the hashed password
    password = Column(String)