from fastapi import APIRouter, HTTPException, status
from typing import List
import httpx

from config import settings
from db.config import SessionLocal
from models.anime import Gender
from schemas.gender import GenderSchema

gender = APIRouter()

url = f'{settings.base_url_kitsu_api}/genres?page[limit]=70&page[offset]=0'

@gender.get('/', response_model=List[GenderSchema], status_code=status.HTTP_200_OK)
async def list_genders():
    with SessionLocal() as db:
        result = db.query(Gender).all()
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
        with SessionLocal() as db:
            for item in data['data']:                
                gender_exists = db.query(Gender).filter(Gender.id == item['id'])
                
                if gender_exists.first() is not None:
                    continue
                                               
                db_gender = Gender(id=item['id'], name=item['attributes']['name'])
                db.add(db_gender)
                db.commit()
                insert_count += 1

        return {"message": f"{insert_count} Genders Guarded!"}  

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Error HTTP: {e.response.text}")

    except httpx.RequestError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error request HTTP: {str(e)}") 