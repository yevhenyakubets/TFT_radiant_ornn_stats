from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ChampionTraits(Base):
    __tablename__ = "champion_traits"

    champion_id = Column(Integer, ForeignKey("champions.id"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
