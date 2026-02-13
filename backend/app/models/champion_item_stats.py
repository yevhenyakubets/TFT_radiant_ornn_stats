from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base


class ChampionItemStats(Base):
    __tablename__ = "champion_item_stats"

    id = Column(Integer, primary_key=True)

    match_id = Column(String, ForeignKey("matches.match_id"), index=True)

    champion_id = Column(Integer, ForeignKey("champions.id"), index=True)
    item_id = Column(Integer, ForeignKey("items.id"), index=True)

    placement = Column(Integer, nullable=False)

    normalized_patch = Column(String, index=True)
