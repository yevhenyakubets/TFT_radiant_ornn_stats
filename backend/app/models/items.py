from sqlalchemy import Column, Integer, String, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    riot_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)

    description = Column(Text)
    effects = Column(JSON)