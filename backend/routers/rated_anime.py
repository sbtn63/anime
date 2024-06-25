from fastapi import APIRouter, Depends, HTTPException, status
from config.db import engine
from sqlalchemy import select, join, and_, exists
from auth.dependencies import get_current_user
from schemas.user import UserSchema, UserRatedAnimeSchema, UserRatedAnimeUpdateSchema
from models.anime import animes
from models.favorite_list import favorite_list_animes, favorite_lists
from models.user import users, user_rated_animes

rated_anime = APIRouter()

@rated_anime.post('/')
async def user_rated_anime(rated_data : UserRatedAnimeSchema, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == rated_data.anime_id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime no exists")
        
        anime_rated = conn.execute(user_rated_animes.select().where(user_rated_animes.c.anime_id == rated_data.anime_id).where(user_rated_animes.c.user_id == current_user.id)).first()
        
        if not anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime rated!")
        
        if not rated_data.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and  5")
        
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime no exists in to list")
        
        rated_data = rated_data.dict()
        rated_data['user_id'] = current_user.id
        
        conn.execute(user_rated_animes.insert().values(rated_data))
        conn.commit()
        
    return {"message" : "Rated Anime Add"}

@rated_anime.patch('/rating/{id}', status_code=status.HTTP_200_OK)
async def update_rating_anime(id : int , data_rating : UserRatedAnimeUpdateSchema, current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime no exists")
        
        if not data_rating.rating in [1, 2, 3, 4, 5]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Rating in 1 and  5")
        
        anime_rated = conn.execute(user_rated_animes.select().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id)).first()
        
        if anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime no rated!")
        
        conn.execute(user_rated_animes.update().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id).values({'rating' : data_rating.rating}))
        conn.commit()
    
    return {"message" : "Anime change rating"}


@rated_anime.delete('/{id}', status_code=status.HTTP_200_OK)
async def update_rating_anime(id : int , current_user : UserSchema = Depends(get_current_user)):
    with engine.connect() as conn:
        anime = conn.execute(animes.select().where(animes.c.id == id)).first()
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime no exists")
        
        anime_rated = conn.execute(user_rated_animes.select().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id)).first()
        
        if anime_rated is None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anime no rated!")
        
        conn.execute(user_rated_animes.delete().where(user_rated_animes.c.anime_id == id).where(user_rated_animes.c.user_id == current_user.id))
        conn.commit()
    
    return {"message" : "Rated anime delete!"}
        
        