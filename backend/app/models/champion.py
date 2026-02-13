from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from app.database import Base

class Champion(Base):
    __tablename__ = "champions"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    cost = Column(Integer)