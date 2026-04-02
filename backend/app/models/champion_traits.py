from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base


class ChampionTraits(Base):
    __tablename__ = "champion_traits"

    champion_id = Column(Integer, ForeignKey("champions.id"), primary_key=True)
    trait_id = Column(Integer, ForeignKey("traits.id"), primary_key=True)
