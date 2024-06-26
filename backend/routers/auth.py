from fastapi import APIRouter, status, HTTPException, Depends
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

from config.db import engine
from auth.dependencies import get_user_email_or_username
from utils.token import create_access_token
from models.user import users
from schemas.user import UserLoginSchema, UserRegisterSchema, UserSchema

auth = APIRouter()

@auth.post('/login', status_code=status.HTTP_200_OK)
async def login_user(login_data : UserLoginSchema):
    user = get_user_email_or_username(login_data.email)    
    if(user is None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not exists!")
        
    check_password = check_password_hash(user.password, login_data.password)
    if not check_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect!")
    
    access_token, access_token_expires = create_access_token(user.username)
    return {"access_token": access_token, "token_type": "Bearer", "expire" : access_token_expires}

@auth.post('/register', status_code=status.HTTP_201_CREATED)
async def register_user(register_data : UserRegisterSchema):
    with engine.connect() as conn:
        if register_data.password != register_data.password_confirmation:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords not match!")
            
        email_exists = get_user_email_or_username(email=register_data.email)
        if(not email_exists is None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email exists!")
            
        username_exists = get_user_email_or_username(username=register_data.username)
        if(not username_exists is None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists!")
        
        register_data.password = generate_password_hash(register_data.password, "pbkdf2:sha256:30", 30)
        register_data = {name: content for name, content in register_data if name != 'password_confirmation'}
        result = conn.execute(users.insert().values(register_data))
        conn.commit()
            
        last_inserted_id = result.inserted_primary_key[0]
        user = conn.execute(users.select().where(users.c.id == last_inserted_id)).fetchone()
            
        access_token, access_token_expires = create_access_token(user.username)
            
    return {"access_token": access_token, "token_type": "Bearer", "expire" : access_token_expires}
