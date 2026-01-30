from fastapi import APIRouter

from app.services.riot_service import get_matches
from app.utils.match_ids import load_match_ids
from app.services.stats_service import (
    extract_units,
    group_units_by_champion,
    count_special_items,
    calculate_average_placement,
    split_special_items_by_type,
    sort_special_items_by_avg_placement,
    extract_all_items,
    get_champion_special_items,
    group_special_items_by_item,
    build_stats,
)

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/matches")
def debug_matches():
    stats = build_stats()

    return {
        "matches_fetched": len(stats["matches"]),
        "first_match_keys": list(stats["matches"][0].keys())
    }


@router.get("/units")
def debug_units():
    stats = build_stats()

    return {
        "units_found": len(stats["units"]),
        "sample": stats["units"][:20]
    }


@router.get("/champions")
def debug_champions():
    stats = build_stats()
    grouped = stats["grouped"]

    return {
        "champion_count": len(grouped),
        "sample": {
            champ: grouped[champ][:2]
            for champ in list(grouped.keys())[:3]
        }
    }


@router.get("/special-items")
def debug_special_items():
    stats = build_stats()

    return {
        "champions_with_special_items": len(stats["special_items"]),
        "sample": dict(list(stats["special_items"].items())[:10])
    }


@router.get("/all-items")
def debug_all_items():
    stats = build_stats()
    all_items = extract_all_items(stats["matches"])

    return {
        "total_unique_items": len(all_items),
        "items": all_items
    }


@router.get("/champions/{champion_name}")
def get_champion_items(champion_name: str):
    stats = build_stats()

    champion_data = get_champion_special_items(
        stats["special_items"],
        champion_name
    )

    if champion_data is None:
        return {"error": "Champion not found"}

    return champion_data


@router.get("/items/{item_name}")
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
