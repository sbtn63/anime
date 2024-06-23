from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FavoriteListSchema(BaseModel):
    id : int = None
    name : str
    description : Optional[str] = None
    cover_url : Optional[str] = None
    created_at : datetime = datetime.utcnow()
    updated_at : Optional[datetime] = None
    user_id : int

class FavoriteListAddSchema(BaseModel):
    name : str
    description : Optional[str] = None
    cover_url : Optional[str] = None
    created_at : datetime = datetime.utcnow()