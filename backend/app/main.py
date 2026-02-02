from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import debug
from app.data.champions import CHAMPIONS

from app.services.stats_service import (
    get_champion_special_items,
    group_special_items_by_item,
    build_stats,
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
        "count": len(CHAMPIONS),
        "champions": sorted(
            CHAMPIONS.values(),
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


@app.get("/items/{item_name}")
def debug_item(item_name: str):
    stats = build_stats()

    items_index = group_special_items_by_item(
        stats["special_items"]
    )

    if item_name not in items_index:
        return {"error": "Item not found"}

    return {
        "item": item_name,
        **items_index[item_name]
    }

