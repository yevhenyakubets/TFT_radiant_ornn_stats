import os
import requests

API_KEY = os.getenv("RIOT_API_KEY")

DARKIN_ARTIFACTS = {
    "TFT16_TheDarkinStaff",
    "TFT16_TheDarkinBow",
    "TFT16_TheDarkinScythe",
}

def get_match(match_id: str):
    headers = {"X-Riot-Token": API_KEY}
    url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}"
    r = requests.get(url, headers=headers)
    return r.json()

def extract_units(match_json):
    result = []

    for player in match_json["info"]["participants"]:
        for unit in player["units"]:
            result.append({
                "champion": unit["character_id"],
                "items": [
                    {
                        "name": item,
                        "type": classify_item(item)
                    }
                    for item in unit["itemNames"]
                ],
                "tier": unit["tier"]
            })

    return result

def classify_item(item_id: str) -> str:
    if "Radiant" in item_id:
        return "radiant"

    if "Artifact" in item_id or item_id in DARKIN_ARTIFACTS:
        return "artifact"

    return "normal"
