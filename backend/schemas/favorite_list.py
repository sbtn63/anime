from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FavoriteListSchema(BaseModel):
    id : int = None
    name : str
    description : Optional[str] = None
    cover_url : Optional[str] = None
    created_at : Optional[datetime] = None
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

class FavoriteListAnimeSchema(BaseModel):
    favorite_list_id : int
    anime_id : int
    created_at : Optional[datetime] = None
    updated_at : Optional[datetime] = None
    
class FavoriteListAnimeAddSchema(BaseModel):
    anime_id : int