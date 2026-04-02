from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, nullable=False)

    name = Column(String, nullable=False)
    cost = Column(Integer)
    ability_name = Column(String)
    ability_desc = Column(Text)
    ability_variables = Column(JSON)
    traits = relationship("Trait", secondary="champion_traits", back_populates="champions")
