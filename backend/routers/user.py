from fastapi import APIRouter, status, Depends, HTTPException
from werkzeug.security import generate_password_hash, check_password_hash

from db.config import SessionLocal, update_model
from auth.dependencies import get_current_user, get_user_email_or_username
from utils.token import create_access_token
from schemas.user import UserSchema, UserUpdateSchema, UserUpdatePasswordSchema

user = APIRouter()

@user.get('/profile', response_model=UserSchema, status_code=status.HTTP_200_OK)
async def profile(current_user : UserSchema = Depends(get_current_user)):
    return current_user

@user.put('/', status_code=status.HTTP_200_OK)
async def update_user(user_data : UserUpdateSchema, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        access_token = None
        
        if not user_data.email is None:
            email_exists = get_user_email_or_username(email=user_data.email)
            if(not email_exists is None):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email exists!")
         
        if not user_data.username is None:   
            username_exists = get_user_email_or_username(username=user_data.username)
            if(not username_exists is None):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username exists!")
            access_token, access_token_expires = create_access_token(user_data.username)
        
        user_data = user_data.dict(exclude_unset=True)
        
        current_user = update_model(instance=current_user, data=user_data)
        
        db.add(current_user)
        db.commit()
        
    if not access_token is None:
        return {"message" : "User Updated!", "access_token": access_token, "token_type": "Bearer", "expire" : access_token_expires}
    else:
        return {"message" : "User Updated!"}

@user.patch('/password', status_code=status.HTTP_200_OK)
async def update_password(data_update_password : UserUpdatePasswordSchema, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        
        if data_update_password.confirm_new_password != data_update_password.new_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords not match!")
        
        check_password = check_password_hash(current_user.password, data_update_password.password)
        if not check_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password incorrect!")
        
        data_update_password.new_password = generate_password_hash(data_update_password.new_password, "pbkdf2:sha256:30", 30)
        
        current_user.password = data_update_password.new_password
        db.add(current_user)
        db.commit()
    
    return {"message" : "Password updated!"}

