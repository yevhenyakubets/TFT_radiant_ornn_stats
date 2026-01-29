import os
import requests
from typing import List

API_KEY = os.getenv("RIOT_API_KEY")

exceptions = {
    "TFT16_TheDarkinStaff",
    "TFT16_TheDarkinBow",
    "TFT16_TheDarkinScythe",
    "TFT16_TheDarkinAegis",
    "TFT7_Item_ShimmerscaleGamblersBlade",
    "TFT7_Item_ShimmerscaleMogulsMail",
}

def get_match(match_id: str):
    headers = {"X-Riot-Token": API_KEY}
    url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}"
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()

def get_matches(match_ids: List[str]) -> List[dict]:
    matches = []
    for match_id in match_ids:
        matches.append(get_match(match_id))
    return matches

def classify_item(item_id: str) -> str:
    if "Radiant" in item_id:
        return "radiant"

    if "Artifact" in item_id or item_id in exceptions or "Ornn" in item_id:
        return "artifact"

    return "normal"
