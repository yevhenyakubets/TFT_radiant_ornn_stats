from sqlalchemy import Column, String, Integer
from app.database import Base


class ChampionStat(Base):
    __tablename__ = "champion_stats"

    champion_id = Column(String, primary_key=True)
    match_id = Column(String, primary_key=True)
    patch = Column(String)
    placement = Column(Integer)
