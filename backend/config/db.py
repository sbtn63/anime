from sqlalchemy import create_engine, MetaData

# Crear motor de base de datos
engine = create_engine("sqlite:///database.db", connect_args={"check_same_thread": False})

# Crear metadatos
meta_data = MetaData()