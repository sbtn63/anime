import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.config import Base

class FavoriteList(Base):
    __tablename__ = "favorite_lists"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    cover_url = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", back_populates="favorite_lists")
    animes = relationship("FavoriteListAnime", back_populates="favorite_list")

class FavoriteListAnime(Base):
    __tablename__ = "favorite_list_animes"
    
    id = Column(Integer, primary_key=True)
    favorite_list_id = Column(Integer, ForeignKey("favorite_lists.id"))
    anime_id = Column(Integer, ForeignKey("animes.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    favorite_list = relationship("FavoriteList", back_populates="animes")
    anime = relationship("Anime", back_populates="favorite_lists")