from sqlalchemy import Table, Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime, Text
from sqlalchemy import ForeignKey
from config.db import meta_data
import datetime

users = Table("users", meta_data,
                Column("id", Integer, primary_key=True),
                Column("username", String(50), nullable=False, unique=True),
                Column("email", String(255), nullable=False, unique=True),
                Column("password", String(255), nullable=False),
                Column("avatar_url", String(255), nullable=True),
                Column("biography", Text, nullable=True),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
            )

user_rated_animes = Table("user_reated_animes", meta_data,
                Column("id", Integer, primary_key=True),
                Column("created_at", DateTime, default=datetime.datetime.utcnow),
                Column("updated_at", DateTime, onupdate=datetime.datetime.utcnow),
                Column("user_id", ForeignKey('users.id')),
                Column("anime_id", ForeignKey('animes.id')),
            )