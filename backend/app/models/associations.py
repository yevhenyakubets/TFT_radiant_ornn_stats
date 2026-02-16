from sqlalchemy import Table, Column, Integer, ForeignKey
from app.database import Base

champion_traits = Table(
    "champion_traits",
    Base.metadata,
    Column("champion_id", Integer, ForeignKey("champions.id"), primary_key=True),
    Column("trait_id", Integer, ForeignKey("traits.id"), primary_key=True),
)