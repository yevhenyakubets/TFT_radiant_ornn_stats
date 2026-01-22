import os
import requests

API_KEY = os.getenv("RIOT_API_KEY")

def get_match(match_id: str):
    headers = {"X-Riot-Token": API_KEY}
    url = f"https://europe.api.riotgames.com/tft/match/v1/matches/{match_id}"
    r = requests.get(url, headers=headers)
    return r.json()