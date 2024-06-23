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

class UserLoginSchema(BaseModel):
    email : EmailStr
    password : str

class UserRegisterSchema(UserLoginSchema):
    username : str
    password_confirmation: str