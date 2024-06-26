import jwt
from datetime import datetime, timedelta
from jwt.exceptions import InvalidTokenError
from config import settings

def create_access_token(username):
    to_encode = {"sub" : username}
    expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key_jwt, algorithm=settings.algorithm)
    return encoded_jwt, expires_delta

def verify_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, settings.secret_key_jwt, algorithms=[settings.algorithm])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception
    return email