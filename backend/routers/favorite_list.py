from fastapi import APIRouter, status, HTTPException, Depends
from typing import List
from datetime import datetime
import httpx

from config import settings
from db.config import SessionLocal, update_model
from auth.dependencies import get_current_user
from models.anime import Anime, AnimeGender
from models.favorite_list import FavoriteList, FavoriteListAnime
from schemas.user import UserSchema
from schemas.favorite_list import FavoriteListSchema, FavoriteListAddSchema, FavoriteListUpdateSchema, FavoriteListAnimeSchema, FavoriteListAnimeAddSchema

favorite_list = APIRouter()
url = f'{settings.base_url_kitsu_api}/anime'

def get_favorite_list(favorite_list_id : int, user_id : int):
    with SessionLocal() as db:        
        result = db.query(FavoriteList).filter(
            FavoriteList.id == favorite_list_id, 
            FavoriteList.user_id == user_id
        ).first()
        
    return result

def convert_to_datetime(date_str : str):
    if date_str is None:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')

@favorite_list.get('/', response_model=List[FavoriteListSchema], status_code=status.HTTP_200_OK)
async def read_favorite_lists(current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        result = db.query(FavoriteList).filter(
            FavoriteList.user_id == current_user.id
        ).all()
        
    return result

@favorite_list.get('/{id}', response_model=FavoriteListSchema, status_code=status.HTTP_200_OK)
async def show_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    result = get_favorite_list(favorite_list_id=id, user_id=current_user.id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
    
    return result

@favorite_list.post('/', response_model=FavoriteListSchema, status_code=status.HTTP_201_CREATED)
async def create_favorite_list(favorite_list_data : FavoriteListAddSchema, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:        
        db_favorite_list = FavoriteList(
            name = favorite_list_data.name,
            description = favorite_list_data.description,
            cover_url = favorite_list_data.cover_url,
            user_id = current_user.id
        )
        db.add(db_favorite_list)
        db.commit()
        
        new_favorite_list = get_favorite_list(favorite_list_id=db_favorite_list.id, user_id=current_user.id)
        
    return new_favorite_list

@favorite_list.put('/{id}', response_model=FavoriteListSchema, status_code=status.HTTP_200_OK)
async def update_favorite_list(id: int, favorite_list_data: FavoriteListUpdateSchema, current_user: UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        result = get_favorite_list(favorite_list_id=id, user_id=current_user.id)
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
        
        update_data = favorite_list_data.dict(exclude_unset=True)
        
        favorite_list = update_model(instance=result, data=update_data)
        db.add(favorite_list)
        db.commit()
        
        updated_favorite_list = get_favorite_list(favorite_list_id=favorite_list.id, user_id=current_user.id)

    return updated_favorite_list

@favorite_list.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_favorite_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        result = get_favorite_list(favorite_list_id=id, user_id=current_user.id)
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
        
        db.delete(result)
        db.commit()
    return {"message" : "Favorite list deleted!"}

@favorite_list.get('/{id}/anime', response_model=List[FavoriteListAnimeSchema], status_code=status.HTTP_200_OK)
async def favorite_list_animes_list(id : int, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        favorite_list = get_favorite_list(favorite_list_id=id, user_id=current_user.id)
        
        if favorite_list is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
    
        result = db.query(FavoriteListAnime).filter(
            FavoriteListAnime.favorite_list_id == id
        ).all()
    
    return result
          
@favorite_list.post('/{id}/anime', status_code=status.HTTP_200_OK)
async def add_anime_favorite_list( id : int, add_anime_favorite_data : FavoriteListAnimeAddSchema, current_user : UserSchema = Depends(get_current_user)):  
    try:
        favorite_list_id = id
        result = get_favorite_list(favorite_list_id=favorite_list_id, user_id=current_user.id)
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
        
        anime_id = add_anime_favorite_data.anime_id
        
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            response_anime = await client.get(f'{url}/{anime_id}', headers=headers)
            
            if response_anime.status_code == 200:
                data_anime = response_anime.json().get('data')
                if data_anime is None:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime does not exist!")
                
                response_genres = await client.get(f'{url}/{anime_id}/relationships/genres', headers=headers)
                if response_genres.status_code == 200:
                    data_genres = response_genres.json().get('data', [])
                else:
                    data_genres = []
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime does not exist!")
        
        with SessionLocal() as db:            
            exist_anime_list = db.query(FavoriteListAnime).filter(
                FavoriteListAnime.anime_id == data_anime['id'],
                FavoriteListAnime.favorite_list_id == favorite_list_id
            )
            
            if exist_anime_list.first():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Anime already in list!")
            
            anime_exists = db.query(Anime).filter(Anime.id == data_anime['id'])
            
            if anime_exists.first() is None:
                db_anime = Anime(
                    id = data_anime['id'],
                    name = data_anime['attributes']['titles'].get('en_jp', ''),
                    description = data_anime['attributes'].get('description', ''),
                    synopsis = data_anime['attributes'].get('synopsis', ''),
                    image_url = data_anime['attributes']['posterImage'].get('small', ''),
                    episodes = data_anime['attributes'].get('episodeCount', 0),
                    start_date = convert_to_datetime(data_anime['attributes'].get('startDate')),
                    end_date = convert_to_datetime(data_anime['attributes'].get('endDate')),
                    status = data_anime['attributes'].get('status', '')
                )
                
                db.add(db_anime)
                
                for item in data_genres:
                    db_gender = AnimeGender(anime_id=anime_id, gender_id=item['id'])
                    db.add(db_gender)
        
            db_favorite_list_animes = FavoriteListAnime(
                anime_id=add_anime_favorite_data.anime_id, 
                favorite_list_id=favorite_list_id
            )
            db.add(db_favorite_list_animes)
            
            db.commit()
            db.refresh(db_favorite_list_animes)
        
        return {"message": "Anime added to list!"}
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error HTTP: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error request HTTP: {str(e)}")

@favorite_list.delete('/{favorite_list_id}/anime/{anime_id}', status_code=status.HTTP_200_OK)
async def delete_anime_favorite_list(favorite_list_id : int, anime_id : int, current_user : UserSchema = Depends(get_current_user)):
    result = get_favorite_list(favorite_list_id, current_user.id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Favorite list not exists!")
    
    with SessionLocal() as db:
        anime = db.query(Anime).filter(Anime.id == anime_id)
        if anime.first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        anime_favorite_list = db.query(FavoriteListAnime).filter(
            FavoriteListAnime.favorite_list_id == favorite_list_id,
            FavoriteListAnime.anime_id == anime_id
        ).first()
        
        if anime_favorite_list is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists into lists!")
        
        db.delete(anime_favorite_list)
        db.commit()
    
    return {"message" : "Anime Deleted!"}