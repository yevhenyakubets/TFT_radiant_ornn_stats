from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base


class Trait(Base):
    __tablename__ = "traits"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, index=True)
    name = Column(String)
    type = Column(String)
    
    champions = relationship("Champion", secondary="champion_traits", back_populates="traits")