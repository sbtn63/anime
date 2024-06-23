from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from config.db import engine
from schemas.favorite_list import FavoriteListSchema, FavoriteListAddSchema, FavoriteListUpdateSchema, FavoriteListAnimeAddSchema
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

@favorite_list.put('/{id}', response_model=FavoriteListSchema, status_code=status.HTTP_200_OK)
async def update_favorite_list(id: int, favorite_list_data: FavoriteListUpdateSchema, current_user: UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.id == id).where(favorite_lists.c.user_id == current_user.id)).fetchone()

        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists")

        update_data = favorite_list_data.dict(exclude_unset=True)
        conn.execute(favorite_lists.update().where(favorite_lists.c.id == id).values(update_data))
        conn.commit()

        updated_favorite_list = conn.execute(favorite_lists.select().where(favorite_lists.c.id == id)).fetchone()

        return updated_favorite_list

@favorite_list.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.id == id).where(favorite_lists.c.user_id == current_user.id)).first()
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list no exists")
        
        conn.execute(favorite_lists.delete().where(favorite_lists.c.id == id))
        conn.commit()
        return {"message" : "Favorite list deleted!"}
           
@favorite_list.post('/anime')
async def add_anime_favorite_list(add_anime_favorite_data : FavoriteListAnimeAddSchema, current_user : UserSchema = Depends(get_current_user)):
    return {"message" : "API"}

@favorite_list.delete('/{favorite_list_id}/anime/{anime_id}')
async def delete_anime_favorite_list():
    return {"message" : "API"}