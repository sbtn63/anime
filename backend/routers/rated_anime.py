from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy import select, join

from db.config import engine
from auth.dependencies import get_current_user
from models.anime import animes
from models.favorite_list import favorite_list_animes, favorite_lists
from models.user import users, user_rated_animes
from schemas.user import UserSchema, UserRatedAnimeSchema, UserRatedAnimeAddSchema, UserRatedAnimeUpdateSchema

rated_anime = APIRouter()

def get_anime_user_rated(anime_id : int , user_id : int):
    with engine.connect() as conn:
        anime_rated = conn.execute(user_rated_animes.select()
            .where(user_rated_animes.c.anime_id == anime_id)
            .where(user_rated_animes.c.user_id == user_id)
        ).first()
        
    return anime_rated

@rated_anime.get('/', response_model=List[UserRatedAnimeSchema], status_code=status.HTTP_200_OK)
async def list_rated_animes_user(current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        result = conn.execute(user_rated_animes.select().where(user_rated_animes.c.user_id == current_user.id)).fetchall()
    return result

@rated_anime.post('/')
async def user_rated_anime(rated_data : UserRatedAnimeAddSchema , current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == rated_data.anime_id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        anime_rated = get_anime_user_rated(anime_id=rated_data.anime_id, user_id=current_user.id)
        if not anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime rated!")
        
        if not rated_data.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and 5!")
        
        query = (
            select(users, favorite_lists, favorite_list_animes)
            .select_from(
                users.join(favorite_lists, users.c.id == favorite_lists.c.user_id)
                    .join(favorite_list_animes, favorite_lists.c.id == favorite_list_animes.c.favorite_list_id)
            )
            .where(favorite_lists.c.user_id == current_user.id)
            .where(favorite_list_animes.c.anime_id == rated_data.anime_id)
        )

        result = conn.execute(query).fetchall()
        
        if len(result) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists in to lists!")
        
        rated_data = rated_data.dict()
        rated_data['user_id'] = current_user.id
        
        conn.execute(user_rated_animes.insert().values(rated_data))
        conn.commit()
        
    return {"message" : "Rated Anime Add!"}

@rated_anime.patch('/{id}/rating', status_code=status.HTTP_200_OK)
async def update_rating_anime(id : int , data_rating : UserRatedAnimeUpdateSchema, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        if not data_rating.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and 5!")
        
        anime_rated = get_anime_user_rated(anime_id=id, user_id=current_user.id)
        if anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime not rated!")
        
        conn.execute(user_rated_animes.update().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id).values({'rating' : data_rating.rating}))
        conn.commit()
    
    return {"message" : "Anime change rating!"}


@rated_anime.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_rated_anime(id : int , current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        anime_rated = get_anime_user_rated(anime_id=id, user_id=current_user.id)
        if anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime not rated!")
        
        conn.execute(user_rated_animes.delete().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id))
        conn.commit()
    
    return {"message" : "Rated anime delete!"}
        
        