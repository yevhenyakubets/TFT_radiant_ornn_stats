from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import joinedload
from app.database import SessionLocal
from app.models.champion import Champion
from app.models.traits import Trait
from app.services.stats_service import get_champion_special_items, get_sorted_traits

router = APIRouter(
    prefix="/champions",
    tags=["champions"]
)

@router.get("/")
def get_champions():
    db = SessionLocal()
    champions = db.query(Champion).options(joinedload(Champion.traits)).all()
    
    result = [
        {
            "id": champ.riot_id,
            "name": champ.name,
            "cost": champ.cost,
            "traits": get_sorted_traits(champ.traits),
        }
        for champ in champions
    ]
    db.close()
    return {"count": len(result), "champions": sorted(result, key=lambda c: c["name"])}

@router.get("/{champion_id}")
def get_champion_items(champion_id: str):
    data = get_champion_special_items(champion_id)
    if not data:
        raise HTTPException(status_code=404, detail="Champion not found")
    return data