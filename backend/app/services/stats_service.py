from typing import List, Dict
from collections import defaultdict
from app.services.riot_service import classify_item

def extract_units(matches: List[dict]) -> List[Dict]:
    units = []

    for match in matches:
        for player in match["info"]["participants"]:
            player_placement = player["placement"]  # get placement from the player

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
                    "items": classified_items,
                    "placement": player_placement  # <-- MUST assign this
                })

    return units

def group_units_by_champion(units: list[dict]) -> dict[str, list[dict]]:
    grouped = defaultdict(list)

    for unit in units:
        grouped[unit["character_id"]].append(unit)

    return grouped

def count_special_items(grouped_units: dict[str, list[dict]]) -> dict:
    result = {}

    for champion, units in grouped_units.items():
        item_counts = defaultdict(lambda: {"count": 0, "placements": []})

        for unit in units:
            for item in unit["items"]:
                if item["type"] in ("radiant", "artifact"):
                    item_data = item_counts[item["item_id"]]
                    item_data["count"] += 1
                    item_data["placements"].append(unit["placement"])

        if item_counts:
            result[champion] = dict(item_counts)

    return result
