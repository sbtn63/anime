from fastapi import status, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_

from db.config import SessionLocal
from utils.token import verify_token
from models.user import User

#Protected routes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#get user auth
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token, credentials_exception)
    user = get_user_email_or_username(username=username)
    if user is None:
        raise HTTPException(status_code=404, detail="User no exists!")
    return user

def get_user_email_or_username(email:str = None, username:str = None):
    if not email and not username:
        return None
    
    with SessionLocal() as db:
        user = db.query(User).filter(
            or_(User.username == username, User.email == email)
        ).first()
    return user