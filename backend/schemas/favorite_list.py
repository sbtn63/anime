from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from schemas.user import UserSchema

class FavoriteListSchema(BaseModel):
    id : int = None
    name : str
    description : Optional[str] = None
    cover_url : Optional[str] = None
    created_at : datetime = datetime.utcnow()
    updated_at : Optional[datetime] = None
    user_id : int

class FavoriteListUpdateSchema(BaseModel):
    name : Optional[str] = None
    description : Optional[str] = None
    cover_url : Optional[str] = None

class FavoriteListAddSchema(BaseModel):
    name : str
    description : Optional[str] = None
    cover_url : Optional[str] = None
    
class FavoriteListAnimeAddSchema(BaseModel):
    favorite_list_id : int
    anime_id : int