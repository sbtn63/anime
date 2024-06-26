from sqlalchemy import create_engine, MetaData
from config import settings

# Crear motor de base de datos
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

# Crear metadatos
meta_data = MetaData()