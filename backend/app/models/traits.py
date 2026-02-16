from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import champion_traits

class Trait(Base):
    __tablename__ = "traits"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, index=True)
    name = Column(String)
    description = Column(Text)
    effects = Column(JSON) # Thresholds/breakpoints

    # Relationship back to Champion
    champions = relationship("Champion", secondary=champion_traits, back_populates="traits")