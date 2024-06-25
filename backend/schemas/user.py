from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    biography: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S") if v else None
        }

class UserUpdateSchema(BaseModel):
    username: Optional[str] =None
    email: Optional[str] = None
    biography: Optional[str] = None
    avatar_url: Optional[str] = None

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : str
    
class UserUpdatePasswordSchema(BaseModel):
    password : str
    new_password : str
    confirm_new_password : str

class UserRegisterSchema(UserLoginSchema):
    username : str
    password_confirmation: str

class UserRatedAnimeSchema(BaseModel):
    id : int
    rating : int
    anime_id : int
    user_id : int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserRatedAnimeAddSchema(BaseModel):
    anime_id : int
    rating : int

class UserRatedAnimeUpdateSchema(BaseModel):
    anime_id : int
    rating : int