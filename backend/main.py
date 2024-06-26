from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from db.config import meta_data, engine
from models.user import users, user_rated_animes
from models.favorite_list import favorite_lists, favorite_list_animes
from models.anime import animes, genders, anime_genders
from routers import auth, user, gender, favorite_list, rated_anime

meta_data.create_all(engine, tables=[users, animes, genders, anime_genders, favorite_lists, favorite_list_animes, user_rated_animes])

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=settings.allowed_credentials,
    allow_methods=settings.allowed_methods.split(","),
    allow_headers=settings.allowed_headers.split(",")
)

app.include_router(auth.auth, prefix='/api/auth', tags=['Auth'])
app.include_router(user.user, prefix='/api/user', tags=['User'])
app.include_router(rated_anime.rated_anime, prefix='/api/rated-anime', tags=['Rated anime'])
app.include_router(favorite_list.favorite_list, prefix='/api/favorite-list', tags=['Favorite List'])
app.include_router(gender.gender, prefix='/api/gender', tags=['Gender'])

@app.get('/')
def hello():
    return {"message" : "API"}