from typing import List, Dict
from collections import defaultdict
from app.services.riot_service import classify_item

def extract_units(matches: List[dict]) -> List[Dict]:
    units = []

    for match in matches:
        for player in match["info"]["participants"]:
            for unit in player.get("units", []):
                classified_items = [
                    {
                        "item_id": item,
                        "type": classify_item(item)
                    }
                    for item in unit.get("itemNames", [])
                ]

                units.append({
                    "character_id": unit["character_id"],
                    "tier": unit["tier"],
                    "items": classified_items
                })

    return units

def group_units_by_champion(units: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)

    for unit in units:
        grouped[unit["character_id"]].append(unit)

    return grouped