from fastapi import FastAPI

from config.db import meta_data, engine
from models.user import users, user_rated_animes
from models.favorite_list import favorite_lists, favorite_list_animes
from models.anime import animes, genders, anime_genders
from routers import auth, user, gender

meta_data.create_all(engine, tables=[users, animes, genders, anime_genders, favorite_lists, favorite_list_animes, user_rated_animes])

app = FastAPI()

app.include_router(auth.auth, prefix='/api/auth', tags=['auth'])
app.include_router(user.user, prefix='/api/user', tags=['user'])
app.include_router(gender.gender, prefix='/api/gender', tags=['gender'])

@app.get('/')
def hello():
    return {"message" : "API"}