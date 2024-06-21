from fastapi import APIRouter, status, Depends
from typing import List
from config.db import engine
from schemas.user import UserSchema
from models.user import users
from auth.dependencies import get_current_user, get_user_email_or_username

user = APIRouter()

@user.get("/profile", response_model=UserSchema)
def profile(current_user : UserSchema = Depends(get_current_user)):
    return current_user

