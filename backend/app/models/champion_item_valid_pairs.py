from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class ChampionItemValidPairs(Base):
    __tablename__ = "champion_item_valid_pairs"

    id = Column(Integer, primary_key=True)

    champion_id = Column(Integer, ForeignKey("champions.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
