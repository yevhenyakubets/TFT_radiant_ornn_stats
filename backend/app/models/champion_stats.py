from sqlalchemy import Column, String, Integer, ForeignKey
from app.database import Base


class ChampionStat(Base):
    __tablename__ = "champion_stats"

    id = Column(Integer, primary_key=True)
    match_id = Column(String, ForeignKey("matches.match_id"), index=True, nullable=False)
    champion_id = Column(Integer, ForeignKey("champions.id"), index=True, nullable=False)  
    puuid = Column(String, index=True, nullable=False)
    
    placement = Column(Integer, nullable=False)
    patch = Column(String, index=True, nullable=False)
