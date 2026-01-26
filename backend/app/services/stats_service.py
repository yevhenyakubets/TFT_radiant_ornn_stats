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

def calculate_average_placement(special_items: dict) -> dict:
    """
    For each champion, calculate the average placement of each special item.
    Returns a similar dict, but each item has an additional 'average_placement' key.
    """
    result = {}

    for champion, items in special_items.items():
        champion_result = {}
        for item_id, item_data in items.items():
            placements = item_data["placements"]
            avg = sum(placements) / len(placements) if placements else None
            champion_result[item_id] = {
                "count": item_data["count"],
                "placements": placements,
                "average_placement": avg
            }
        result[champion] = champion_result

    return result

def sort_items_by_performance(
    special_items: dict[str, dict[str, dict]]
) -> dict[str, list[dict]]:
    """
    Sort items for each champion by average placement (ascending).
    Best item = lowest average placement.
    """

    sorted_result = {}

    for champion, items in special_items.items():
        sorted_items = sorted(
            items.items(),
            key=lambda x: x[1]["average_placement"]
        )

        sorted_result[champion] = [
            {
                "item_id": item_id,
                **data
            }
            for item_id, data in sorted_items
        ]

    return sorted_result