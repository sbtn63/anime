import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.config import Base

class Anime(Base):
    __tablename__ = "animes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    synopsis = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=False)
    episodes = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    favorite_lists = relationship("FavoriteListAnime", back_populates="anime")
    rated_users = relationship("UserRatedAnime", back_populates="anime")
    genders = relationship("AnimeGender", back_populates="anime")

class Gender(Base):
    __tablename__ = "genders"
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    animes = relationship("AnimeGender", back_populates="gender")


class AnimeGender(Base):
    __tablename__ = "anime_genders"
    
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey("animes.id"))
    gender_id = Column(Integer, ForeignKey("genders.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    anime = relationship("Anime", back_populates="genders")
    gender = relationship("Gender", back_populates="animes")