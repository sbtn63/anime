from fastapi import APIRouter

favorite_list = APIRouter()

@favorite_list.get('/')
async def favorite_lists():
    pass

@favorite_list.get('/{id}')
async def favorite_list():
    pass

@favorite_list.post('/')
async def create_favorite_list():
    pass

@favorite_list.post('/add/anime')
async def add_anime_favorite_list():
    pass

@favorite_list.delete('/delete/anime/{id}')
async def delete_anime_favorite_list():
    pass

@favorite_list.put('/{id}')
async def update_favorite_list():
    pass

@favorite_list.delete('/{id}')
async def delete_favorite_list():
    pass