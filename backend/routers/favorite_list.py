from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from config.db import engine
from schemas.favorite_list import FavoriteListSchema, FavoriteListAddSchema
from schemas.user import UserSchema
from auth.dependencies import get_current_user
from models.favorite_list import favorite_lists

favorite_list = APIRouter()

@favorite_list.get('/', response_model=List[FavoriteListSchema], status_code=status.HTTP_200_OK)
async def read_favorite_lists(current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.user_id == current_user.id)).fetchall()
        return result

@favorite_list.get('/{id}', response_model=FavoriteListSchema, status_code=status.HTTP_200_OK)
async def show_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.id == id).where(favorite_lists.c.user_id == current_user.id)).first()
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list no exists")
        
        return result

@favorite_list.post('/', response_model=FavoriteListSchema, status_code=status.HTTP_201_CREATED)
async def create_favorite_list(favorite_list_data : FavoriteListAddSchema, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        favorite_list_data_dict = favorite_list_data.dict()
        favorite_list_data_dict['user_id'] = current_user.id
        
        result = conn.execute(favorite_lists.insert().values(favorite_list_data_dict))
        conn.commit()
        
        last_inserted_id = result.inserted_primary_key[0]
        favorite_list = conn.execute(favorite_lists.select().where(favorite_lists.c.id == last_inserted_id)).fetchone()
        
        return favorite_list

@favorite_list.post('/anime')
async def add_anime_favorite_list():
    return {"message" : "API"}

@favorite_list.delete('/anime/{id}')
async def delete_anime_favorite_list():
    return {"message" : "API"}

@favorite_list.put('/{id}')
async def update_favorite_list():
    return {"message" : "API"}

@favorite_list.delete('/{id}')
async def delete_favorite_list():
    return {"message" : "API"}