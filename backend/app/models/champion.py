from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.associations import champion_traits # Import the Table object

class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Integer)

    ability_name = Column(String)
    ability_desc = Column(Text)
    ability_variables = Column(JSON) # Scaling numbers

    # NEW RELATIONSHIP (Many-to-Many)
    # Using string "Trait" avoids circular import
    traits = relationship("Trait", secondary=champion_traits, back_populates="champions")