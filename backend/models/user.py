import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.config import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column("id", Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar_url = Column(String(255), nullable=True)
    biography = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    favorite_lists = relationship("FavoriteList", back_populates="user")
    rated_animes = relationship("UserRatedAnime", back_populates="user")

class UserRatedAnime(Base):
    __tablename__ = "user_rated_animes"
    
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    anime_id = Column(Integer, ForeignKey('animes.id'))
    
    user = relationship("User", back_populates="rated_animes")
    anime = relationship("Anime", back_populates="rated_users")