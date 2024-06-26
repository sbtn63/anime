from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import datetime

from db.config import meta_data

favorite_lists = Table("favorite_lists", meta_data,
                Column("id", Integer, primary_key=True),
                Column("name", String(50), nullable=False),
                Column("description", Text, nullable=True),
                Column("cover_url", String(255), nullable=True),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
                Column("user_id", ForeignKey('users.id')),
            )

favorite_list_animes = Table("favorite_list_animes", meta_data,
                Column("id", Integer, primary_key=True),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
                Column("favorite_list_id", ForeignKey('favorite_lists.id')),
                Column("anime_id", ForeignKey('animes.id')),
            )