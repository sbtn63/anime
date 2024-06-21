from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GenderSchema(BaseModel):
    id : int = None
    name : str = None
    created_at : datetime = datetime.utcnow()
    updated_at : Optional[datetime] = None