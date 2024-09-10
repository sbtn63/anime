from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from db.config import SessionLocal
from auth.dependencies import get_current_user
from models.anime import Anime
from models.favorite_list import FavoriteListAnime
from models.user import UserRatedAnime
from schemas.user import UserSchema, UserRatedAnimeSchema, UserRatedAnimeAddSchema, UserRatedAnimeUpdateSchema

rated_anime = APIRouter()

def get_anime_user_rated(anime_id : int , user_id : int):
    with SessionLocal() as db:        
        anime_rated = db.query(UserRatedAnime).filter(
            UserRatedAnime.anime_id == anime_id,
            UserRatedAnime.user_id == user_id
        ).first()
        
    return anime_rated

@rated_anime.get('/', response_model=List[UserRatedAnimeSchema], status_code=status.HTTP_200_OK)
async def list_rated_animes_user(current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        result = db.query(UserRatedAnime).filter(UserRatedAnime.user_id == current_user.id).all()
    return result

@rated_anime.post('/{id}')
async def user_rated_anime(id : int, rated_data : UserRatedAnimeAddSchema , current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        anime = db.query(Anime).filter(Anime.id == id).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        anime_rated = get_anime_user_rated(anime_id=id, user_id=current_user.id)
        if not anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime rated!")
        
        if not rated_data.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and 5!")
        
        result = db.query(FavoriteListAnime).filter(
            FavoriteListAnime.favorite_list.has(user=current_user),
            FavoriteListAnime.anime_id == id
        ).first()
        
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists in to lists!")
        
        db_rated = UserRatedAnime(rating=rated_data.rating, anime_id=id, user_id=current_user.id)
        db.add(db_rated)
        db.commit()
        db.refresh(db_rated)
        
    return {"message" : "Rated Anime Add!"}

@rated_anime.patch('/{id}/rating', status_code=status.HTTP_200_OK)
async def update_rating_anime(id : int , data_rating : UserRatedAnimeUpdateSchema, current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        anime = db.query(Anime).filter(Anime.id == id).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not exists!")
        
        if not data_rating.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and 5!")
        
        anime_rated = get_anime_user_rated(anime_id=id, user_id=current_user.id)
        if anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime not rated!")
        
        anime_rated.rating = data_rating.rating
        db.add(anime_rated)
        db.commit()
    
    return {"message" : "Anime change rating!"}


@rated_anime.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_rated(id : int , current_user : UserSchema = Depends(get_current_user)):
    with SessionLocal() as db:
        rated_anime = db.query(UserRatedAnime).filter(
            UserRatedAnime.anime_id == id,
            UserRatedAnime.user_id == current_user.id
        ).first()
        
        if rated_anime is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rated anime not exists!")
        
        db.delete(rated_anime)
        db.commit()
    
    return {"message" : "Rated anime delete!"}
        
        