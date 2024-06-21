from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
import enum
from sqlalchemy import Enum
from config.db import meta_data
import datetime

class SeasonEnum(enum.Enum):
    SPRING = 'Spring'
    SUMMER = 'Summer'
    AUTUMN = 'Autumn'
    WINTER = 'Winter'

animes = Table("animes", meta_data,
                Column("id", Integer, primary_key=True, autoincrement=False),
                Column("name", String(250),nullable=False),
                Column("description", Text, nullable=False),
                Column("synopsis", Text, nullable=False),
                Column("image_url", String(255), nullable=False),
                Column("episodes", Integer, nullable=True),
                Column("start_aired", DateTime, nullable=False),
                Column("end_aired", DateTime, nullable=False),
                Column("premiered", Enum(SeasonEnum), nullable=False),
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