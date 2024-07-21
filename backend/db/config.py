from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import settings

Base = declarative_base()

def update_model(instance, data):
    for key, value in data.items():
        #if hasattr(instance, key):
        setattr(instance, key, value)
    return instance

# Crear motor de base de datos
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)