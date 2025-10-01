# FILE: server/src/api/user.py

from fastapi import APIRouter, Depends
from . import schemas, models
from .security import get_current_user

# The variable MUST be named 'user_router' to match the import in main.py
user_router = APIRouter()

# This is a secure endpoint that gets the currently authenticated user's details.
# It requires a valid token to be sent in the request header.
@user_router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user