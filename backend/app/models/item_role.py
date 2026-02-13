from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ItemRole(Base):
    __tablename__ = "item_roles"

    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id"), primary_key=True)
