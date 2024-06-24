import httpx
from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from config.db import engine
from schemas.favorite_list import FavoriteListSchema, FavoriteListAddSchema, FavoriteListUpdateSchema, FavoriteListAnimeAddSchema
from schemas.user import UserSchema
from auth.dependencies import get_current_user
from models.favorite_list import favorite_lists, favorite_list_animes
from models.anime import animes, anime_genders, genders
from config.settings import BASE_URL_KITSU_API
from datetime import datetime

favorite_list = APIRouter()
url = f'{BASE_URL_KITSU_API}/anime'

def get_favorite_list(favorite_list_id : int, current_user_id : int):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.id == favorite_list_id).where(favorite_lists.c.user_id == current_user_id)).first()
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list no exists")

        return result

def convert_to_datetime(date_str):
    if date_str is None:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')

@favorite_list.get('/', response_model=List[FavoriteListSchema], status_code=status.HTTP_200_OK)
async def read_favorite_lists(current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(favorite_lists.select().where(favorite_lists.c.user_id == current_user.id)).fetchall()
        return result

@favorite_list.get('/{id}', response_model=FavoriteListSchema, status_code=status.HTTP_200_OK)
async def show_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    result = get_favorite_list(id, current_user.id)
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
        result = get_favorite_list(id, current_user.id)
        
        update_data = favorite_list_data.dict(exclude_unset=True)
        conn.execute(favorite_lists.update().where(favorite_lists.c.id == id).values(update_data))
        conn.commit()

        updated_favorite_list = conn.execute(favorite_lists.select().where(favorite_lists.c.id == id)).fetchone()

        return updated_favorite_list

@favorite_list.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = get_favorite_list(id, current_user.id)
        
        conn.execute(favorite_lists.delete().where(favorite_lists.c.id == id))
        conn.commit()
        return {"message" : "Favorite list deleted!"}
           
@favorite_list.post('/anime', status_code=status.HTTP_200_OK)
async def add_anime_favorite_list(add_anime_favorite_data : FavoriteListAnimeAddSchema, current_user : UserSchema = Depends(get_current_user)):  
    try:
        anime_id = add_anime_favorite_data.anime_id
        favorite_list_id = add_anime_favorite_data.favorite_list_id
        
        result = get_favorite_list(favorite_list_id, current_user.id)
        
        headers = {
            "Content-Type": "application/json",
        }
        
        async with httpx.AsyncClient() as client:
            response_anime = await client.get(f'{url}/{anime_id}', headers=headers)
            
            if response_anime.status_code == 200:
                data_anime = response_anime.json()
                response_geners = await client.get(f'{url}/{anime_id}/relationships/genres', headers=headers)
                if response_geners.status_code == 200:
                    data_genders = response_geners.json()
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime no exists")
        
        with engine.begin() as conn:
            data_anime = data_anime['data']
            
            exist_anime_list = conn.execute(favorite_list_animes.select().where(favorite_list_animes.c.anime_id == data_anime['id']).where(favorite_list_animes.c.favorite_list_id == favorite_list_id))
            if not exist_anime_list.first() is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime exists list")
            
            anime_exists = conn.execute(animes.select().where(animes.c.id == data_anime['id']))
                
            if anime_exists.first() is None:
                anime_data = {
                    "id" : data_anime['id'],
                    "name" : data_anime['attributes']['titles']['en_jp'],
                    "description" : data_anime['attributes']['description'],
                    "synopsis" : data_anime['attributes']['synopsis'],
                    "image_url" : data_anime['attributes']['posterImage']['small'],
                    "episodes" : data_anime['attributes']['episodeCount'],
                    "start_date" : convert_to_datetime(data_anime['attributes']['startDate']),
                    "end_date" : convert_to_datetime(data_anime['attributes']['endDate']),
                    "status" : data_anime['attributes']['status']
                }
                
                conn.execute(animes.insert().values(anime_data))
                    
                for item in data_genders['data']:
                    gender = conn.execute(genders.select().where(genders.c.id == item['id']))
                        
                    if gender.first() is None:                   
                        continue
                        
                    anime_gender = {"anime_id" : anime_id, "gender_id" : item['id']}                                         
                    conn.execute(anime_genders.insert().values(anime_gender))
                    
            conn.execute(favorite_list_animes.insert().values(add_anime_favorite_data.dict()))
        return {"message" : "Anime add list"}

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error HTTP: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error de solicitud HTTP: {str(e)}")

@favorite_list.delete('/{favorite_list_id}/anime/{anime_id}')
async def delete_anime_favorite_list():
    return {"message" : "API"}