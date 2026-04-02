from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base


class ChampionRole(Base):
    __tablename__ = "champion_roles"

    champion_id = Column(Integer, ForeignKey("champions.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
