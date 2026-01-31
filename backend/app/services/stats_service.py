from typing import List, Dict
from collections import defaultdict

from app.services.riot_service import classify_item
from app.data.radiant_items import CHAMPION_RADIANT_ITEMS
from app.data.artifacts import CHAMPION_ARTIFACTS
from app.services.cache import CACHE
from app.services.riot_service import get_matches
from app.utils.match_ids import load_match_ids

def build_stats():
    """
    Builds and caches all derived stats used by endpoints.
    """
    cache_key = "FULL_STATS"

    if cache_key in CACHE:
        return CACHE[cache_key]

    match_ids = load_match_ids()
    matches = get_matches(match_ids)

    units = extract_units(matches)
    grouped = group_units_by_champion(units)
    counts = count_special_items(grouped)
    with_avg = calculate_average_placement(counts)
    split_items = split_special_items_by_type(with_avg)
    split_sorted = sort_special_items_by_avg_placement(split_items)

    data = {
        "matches": matches,
        "units": units,
        "grouped": grouped,
        "special_items": split_sorted,
    }

    CACHE[cache_key] = data
    return data


def champion_id_to_name(champion_id: str) -> str:
    return champion_id.split("_", 1)[1]

def normalize_item_name(item_id: str) -> str:
    """
    Converts item id like:
    TFT9_Item_OrnnHullbreaker -> OrnnHullbreaker
    TFT5_Item_WarmogsArmorRadiant -> WarmogsArmorRadiant
    """
    return item_id.split("_")[-1]


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

def extract_all_items(matches: list[dict]) -> dict:
    """
    Returns all items found in the sample, grouped by raw item_id
    """
    items = {}

    for match in matches:
        for player in match["info"]["participants"]:
            for unit in player.get("units", []):
                for item_id in unit.get("itemNames", []):
                    if item_id not in items:
                        items[item_id] = {
                            "count": 0,
                            "champions": set()
                        }

                    items[item_id]["count"] += 1
                    items[item_id]["champions"].add(unit["character_id"])

    # convert sets to lists for JSON
    for item in items.values():
        item["champions"] = sorted(item["champions"])

    return dict(sorted(items.items()))


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
                item_type = item["type"]
                if item_type not in ("radiant", "artifact"):
                    continue

                item_id = item["item_id"]

                # eligibility filter
                if item_type == "radiant":
                    allowed = CHAMPION_RADIANT_ITEMS.get(champion, [])
                else:  # artifact
                    allowed = CHAMPION_ARTIFACTS.get(champion, [])

                if item_id not in allowed:
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

def get_champion_special_items(split_sorted_items: dict, champion_name: str):
    normalized = champion_name.lower()

    for champion_id, data in split_sorted_items.items():
        if champion_id_to_name(champion_id).lower() == normalized:
            return {
                "champion": champion_id_to_name(champion_id),
                "artifact": data.get("artifact", {}),
                "radiant": data.get("radiant", {})
            }

    return None

def group_special_items_by_item(
    split_items: dict[str, dict]
) -> dict[str, dict]:
    """
    Inverts the structure to:
    {
      item_name: {
        "type": "artifact" | "radiant",
        "champions": {
          champion_id: {
            "count": int,
            "average_placement": float
          }
        }
      }
    }
    """
    result = {}

    for champion, types in split_items.items():
        for item_type, items in types.items():
            for item_id, data in items.items():
                item_name = normalize_item_name(item_id)

                if item_name not in result:
                    result[item_name] = {
                        "type": item_type,
                        "champions": {}
                    }

                result[item_name]["champions"][champion] = {
                    "count": data["count"],
                    "average_placement": data["average_placement"]
                }

    return result
