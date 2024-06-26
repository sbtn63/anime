from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
import datetime

from db.config import meta_data


animes = Table("animes", meta_data,
                Column("id", Integer, primary_key=True, autoincrement=False),
                Column("name", String(250),nullable=False),
                Column("description", Text, nullable=False),
                Column("synopsis", Text, nullable=False),
                Column("image_url", String(255), nullable=False),
                Column("episodes", Integer, nullable=True),
                Column("start_date", DateTime, nullable=True),
                Column("end_date", DateTime, nullable=True),
                Column("status", String(50), nullable=False),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
            )

genders = Table("genders", meta_data,
                Column("id", Integer, primary_key=True, autoincrement=False),
                Column("name", String(100), nullable=False, unique=True),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
            )

anime_genders = Table("anime_genders", meta_data,
                Column("id", Integer, primary_key=True),
                Column("anime_id", ForeignKey('animes.id')),
                Column("gender_id", ForeignKey('genders.id')),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
            )