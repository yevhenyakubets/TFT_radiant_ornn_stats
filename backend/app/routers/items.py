from fastapi import APIRouter, HTTPException
from app.database import SessionLocal
from app.models.items import Item
from app.services.stats_service import get_item_stats_by_id

router = APIRouter(tags=["items"])

@router.get("/radiant-items")
def get_radiant_items():
    db = SessionLocal()
    items = db.query(Item).filter(Item.type == "radiant").all()
    result = {item.riot_id: {"id": item.riot_id, "name": item.name} for item in items}
    db.close()
    return result

@router.get("/artifacts")
def get_artifact_items():
    db = SessionLocal()
    items = db.query(Item).filter(Item.type == "artifact").all()
    result = {item.riot_id: {"id": item.riot_id, "name": item.name} for item in items}
    db.close()
    return result

@router.get("/artifacts/{artifact_id}")
def get_artifact_page(artifact_id: str):
    data = get_item_stats_by_id(artifact_id, "artifact")
    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return data

@router.get("/radiant-items/{radiant_id}")
def get_radiant_page(radiant_id: str):
    data = get_item_stats_by_id(radiant_id, "radiant")
    if not data:
        raise HTTPException(status_code=404, detail="Radiant item not found")
    return data