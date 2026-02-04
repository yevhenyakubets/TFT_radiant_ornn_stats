from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import debug
from app.data.champions import champions
from app.data.artifacts import get_all_artifact_items
from app.data.radiant_items import get_all_radiant_items

from app.services.stats_service import (
    get_champion_special_items,
    build_stats,
    get_artifact_stats_by_name,
)

app = FastAPI()

app.include_router(debug.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/champions")
def get_champions():
    return {
        "count": len(champions),
        "champions": sorted(
            champions.values(),
            key=lambda c: c["name"]
        )
    }


@app.get("/champions/{champion_name}")
def get_champion_items(champion_name: str):
    stats = build_stats()

    champion_data = get_champion_special_items(
        stats["special_items"],
        champion_name
    )

    if champion_data is None:
        return {"error": "Champion not found"}

    return champion_data

@app.get("/radiant-items")
def get_radiant_items():
    from app.data.radiant_items import get_all_radiant_items
    return get_all_radiant_items()

@app.get("/artifacts")
def get_artifact_items():
    from app.data.artifacts import get_all_artifact_items
    return get_all_artifact_items()


@app.get("/artifacts/{artifact_name}")
def get_artifact_page(artifact_name: str):
    stats = build_stats()

    data = get_artifact_stats_by_name(
        stats["special_items"],
        artifact_name
    )

    if not data:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return data