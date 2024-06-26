from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

class Settings(BaseSettings):
    secret_key_jwt: str
    algorithm: str
    access_token_expire_minutes: int
    
    base_url_kitsu_api : str
    
    database_url : str
    
    allowed_origins: str
    allowed_credentials: bool
    allowed_methods: str
    allowed_headers: str

    class Config:
        env_file = ".env"

settings = Settings()