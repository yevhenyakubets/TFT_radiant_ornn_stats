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
        champion_items = {}

        for unit in units:
            placement = unit["placement"]

            for item in unit["items"]:
                if item["type"] not in ("radiant", "artifact"):
                    continue

                item_id = item["item_id"]

                if item_id not in champion_items:
                    champion_items[item_id] = {
                        "count": 0,
                        "placements": [],
                        "type": item["type"]
                    }

                champion_items[item_id]["count"] += 1
                champion_items[item_id]["placements"].append(placement)

        if champion_items:
            result[champion] = champion_items

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
                "average_placement": avg,
                "type": item_data["type"]
            }
        result[champion] = champion_result

    return result

def split_special_items_by_type(
    special_items: dict[str, dict]
) -> dict[str, dict]:
    """
    Splits special items per champion into:
    {
      champion_id: {
        "artifact": { item_id: data },
        "radiant": { item_id: data }
      }
    }
    """
    result = {}

    for champion, items in special_items.items():
        by_type = {
            "artifact": {},
            "radiant": {}
        }

        for item_id, data in items.items():
            item_type = data.get("type")
            if item_type in by_type:
                by_type[item_type][item_id] = data

        # only keep champion if it has at least one item
        if by_type["artifact"] or by_type["radiant"]:
            result[champion] = by_type

    return result

def sort_special_items_by_avg_placement(
    split_items: dict[str, dict]
) -> dict[str, dict]:
    """
    Sorts artifact and radiant items per champion
    by ascending average placement.
    """

    result = {}

    for champion, types in split_items.items():
        sorted_types = {}

        for item_type, items in types.items():
            # items is a dict: item_id -> data
            sorted_items = sorted(
                items.items(),
                key=lambda x: x[1]["average_placement"]
            )

            # convert back to dict, preserving order
            sorted_types[item_type] = {
                item_id: data for item_id, data in sorted_items
            }

        result[champion] = sorted_types

    return result
