from typing import List, Dict

def extract_units(matches: List[dict]) -> List[Dict]:
    units = []

    for match in matches:
        for player in match["info"]["participants"]:
            for unit in player.get("units", []):
                units.append({
                    "character_id": unit["character_id"],
                    "tier": unit["tier"],
                    "items": unit.get("itemNames", [])
                })

    return units
