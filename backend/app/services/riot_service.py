import os
import requests

API_KEY = os.getenv("RIOT_API_KEY")

def get_match(match_id: str):
    headers = {"X-Riot-Token": API_KEY}
    url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}"
    r = requests.get(url, headers=headers)
    return r.json()

def extract_units(match_json):
    result = []

    participants = match_json["info"]["participants"]

    for player in participants:
        for unit in player["units"]:
            result.append({
                "champion": unit["character_id"],
                "items": unit["itemNames"],
                "tier": unit["tier"]
            })

    return result