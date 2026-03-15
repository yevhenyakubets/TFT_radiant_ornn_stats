from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item

from app.services.stats_service import (
    get_champion_special_items,
    get_item_stats_by_id,
    get_sorted_traits,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # TODO: Should be envs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "ok"}


# ================================
# CHAMPIONS LIST
# ================================


@app.get("/champions")
def get_champions():
    db = SessionLocal()

    # Use joinedload to avoid N+1 query problem (loading traits for all champs at once)
    from sqlalchemy.orm import joinedload

    champions = db.query(Champion).options(joinedload(Champion.traits)).all()

    result = [
        {
            "id": champ.riot_id,
            "name": champ.name,
            "cost": champ.cost,
            "traits": get_sorted_traits(champ.traits),  # <--- Added
        }
        for champ in champions
    ]

    db.close()

    return {"count": len(result), "champions": sorted(result, key=lambda c: c["name"])}


# ================================
# CHAMPION PAGE
# ================================


@app.get("/champions/{champion_id}")
def get_champion_items(champion_id: str):
    data = get_champion_special_items(champion_id)

    if not data:
        raise HTTPException(status_code=404, detail="Champion not found")

    return data


# ================================
# ITEMS LIST
# ================================


@app.get("/radiant-items")
def get_radiant_items():
    db = SessionLocal()
    items = db.query(Item).filter(Item.type == "radiant").all()

    result = {
        item.riot_id: {
            "id": item.riot_id,
            "name": item.name,
        }
        for item in items
    }

    db.close()
    return result


@app.get("/artifacts")
def get_artifact_items():
    db = SessionLocal()
    items = db.query(Item).filter(Item.type == "artifact").all()

    result = {
        item.riot_id: {
            "id": item.riot_id,
            "name": item.name,
        }
        for item in items
    }

    db.close()
    return result


# ================================
# ARTIFACT PAGE
# ================================


@app.get("/artifacts/{artifact_id}")
def get_artifact_page(artifact_id: str):
    data = get_item_stats_by_id(artifact_id, "artifact")

    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return data


# ================================
# RADIANT PAGE
# ================================


@app.get("/radiant-items/{radiant_id}")
def get_radiant_page(radiant_id: str):
    data = get_item_stats_by_id(radiant_id, "radiant")

    if not data:
        raise HTTPException(status_code=404, detail="Radiant item not found")

    return data
