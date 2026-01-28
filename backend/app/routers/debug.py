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
)

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/matches")
def debug_matches():
    match_ids = load_match_ids()
    matches = get_matches(match_ids[:2])  # only 2 for safety

    return {
        "match_ids_loaded": len(match_ids),
        "matches_fetched": len(matches),
        "first_match_keys": list(matches[0].keys())
    }

@router.get("/units")
def debug_units():
    match_ids = load_match_ids()
    matches = get_matches(match_ids[:2])
    units = extract_units(matches)

    return {
        "units_found": len(units),
        "sample": units[:20]
    }

@router.get("/champions")
def debug_champions():
    match_ids = load_match_ids()
    matches = get_matches(match_ids)
    units = extract_units(matches)
    grouped = group_units_by_champion(units)

    return {
        "champion_count": len(grouped),
        "sample": {
            champ: grouped[champ][:2]
            for champ in list(grouped.keys())[:3]
        }
    }

@router.get("/special-items")
def debug_special_items():
    match_ids = load_match_ids()
    matches = get_matches(match_ids)
    units = extract_units(matches)
    grouped = group_units_by_champion(units)
    counts = count_special_items(grouped)
    special_with_avg = calculate_average_placement(counts)
    split_items = split_special_items_by_type(special_with_avg)
    split_sorted = sort_special_items_by_avg_placement(split_items)

    return {
        "champions_with_special_items": len(split_sorted),
        "sample": dict(list(split_sorted.items())[:10])
    }

@router.get("/all-items")
def debug_all_items():
    match_ids = load_match_ids()
    matches = get_matches(match_ids)

    all_items = extract_all_items(matches)

    return {
        "total_unique_items": len(all_items),
        "items": all_items
    }
