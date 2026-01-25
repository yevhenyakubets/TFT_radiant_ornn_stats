from fastapi import APIRouter
from app.services.riot_service import get_matches
from app.utils.match_ids import load_match_ids

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
