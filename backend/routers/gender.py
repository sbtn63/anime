from fastapi import APIRouter, HTTPException, status
from typing import List
import httpx

from config.db import engine
from config.settings import BASE_URL_KITSU_API
from models.anime import genders
from schemas.gender import GenderSchema

gender = APIRouter()

url = f'{BASE_URL_KITSU_API}/genres?page[limit]=70&page[offset]=0'

@gender.get('/', response_model=List[GenderSchema], status_code=status.HTTP_200_OK)
async def list_genders():
    with engine.connect() as conn:
        result = conn.execute(genders.select()).fetchall()
    return result

@gender.post('/', status_code=status.HTTP_201_CREATED)
async def create_genders():
    headers = {
        "Content-Type": "application/json",
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

        if 'data' not in data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error server")
            
        insert_count = 0
        with engine.begin() as conn:  # Uso de transacciones
            for item in data['data']:
                gender_exists = conn.execute(
                    genders.select()
                    .where(genders.c.id == item['id'])
                )
                
                if gender_exists.first() is not None:
                    continue
                
                gender_data = {"id" : item['id'], "name" : item['attributes']['name'] }                                       

                conn.execute(genders.insert().values(gender_data))
                insert_count += 1

        return {"message": f"{insert_count} Genders Guarded!"}  

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error HTTP: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error request HTTP: {str(e)}") 