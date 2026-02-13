# backend/scripts/riot_ingest.py

import os
import time
import requests
import argparse

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.match import Match

load_dotenv()

API_KEY = os.getenv("RIOT_API_KEY")

PLATFORM_URL = "https://euw1.api.riotgames.com"
REGIONAL_URL = "https://europe.api.riotgames.com"

HEADERS = {
    "X-Riot-Token": API_KEY
}

def get_existing_match_ids(db):
    rows = db.query(Match.match_id).all()
    return set(r[0] for r in rows)



# ---------- Utility: Safe Request with Rate Handling ----------

def riot_get(url, params=None):
    while True:
        response = requests.get(url, headers=HEADERS, params=params)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Sleeping {retry_after}s")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()


# ---------- Step 1: Get PUUIDs ----------

def get_puuids_by_tier(tier: str, division: str | None):
    if tier in ["challenger", "grandmaster", "master"]:
        url = f"{PLATFORM_URL}/tft/league/v1/challenger?api_key={API_KEY}"
        response = requests.get(url).json()
        return [entry["puuid"] for entry in response["entries"]]
    else:
        # diamond / emerald / platinum
        puuids = []
        page = 1

        while True:
            url = f"{PLATFORM_URL}/tft/league/v1/entries/{tier.upper()}/{division}?page={page}&api_key={API_KEY}"
            response = requests.get(url)
            data = response.json()

            if not data:
                break

            puuids.extend([entry["puuid"] for entry in data])

            print(f"Fetched page {page} - {len(data)} players")

            page += 1

        return puuids


# ---------- Step 2: Get Match IDs ----------

def get_match_ids(puuid, start=0, count=10):
    url = f"{REGIONAL_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids"
    params = {
        "start": start,
        "count": count
    }
    return riot_get(url, params=params)


# ---------- Step 3: Get Match Details ----------

def get_match(match_id):
    url = f"{REGIONAL_URL}/tft/match/v1/matches/{match_id}"
    return riot_get(url)


# ---------- Step 4: Insert Match ----------

def insert_match(db: Session, match_id: str, data: dict):
    existing = db.query(Match).filter(Match.match_id == match_id).first()
    if existing:
        return False

    match = Match(
        match_id=match_id,
        data=data
    )
    db.add(match)
    db.commit()
    return True

def parse_args():
    parser = argparse.ArgumentParser(description="TFT Riot ingestion script")

    parser.add_argument(
        "--tier",
        required=True,
        choices=[
            "challenger",
            "grandmaster",
            "master",
            "diamond",
            "emerald",
            "platinum"
        ],
        help="Rank tier to ingest"
    )

    parser.add_argument(
        "--division",
        choices=["I", "II", "III", "IV"],
        help="Division (required for diamond/emerald/platinum)"
    )

    return parser.parse_args()

# ---------- Main Pipeline ----------

def run():
    db = SessionLocal()


    existing_match_ids = get_existing_match_ids(db)
    print(f"Loaded {len(existing_match_ids)} existing matches from DB")

    args = parse_args()
    tier = args.tier.lower()
    division = args.division

    # Validate division requirement
    if tier in ["diamond", "emerald", "platinum"] and not division:
        raise ValueError("Division is required for Diamond, Emerald and Platinum")

    if tier in ["challenger", "grandmaster", "master"] and division:
        raise ValueError("Division should not be provided for Challenger/GM/Master")

    puuids = get_puuids_by_tier(tier, division)

    print(f"Found {len(puuids)} players in {tier} {division or ''}")

    for puuid in puuids:  # limit for dev key safety
        match_ids = get_match_ids(puuid)

        for match_id in match_ids:
            if match_id in existing_match_ids:
                continue

            match_data = get_match(match_id)
            inserted = insert_match(db, match_id, match_data)

            if inserted:
                print(f"Inserted {match_id}")
            else:
                print(f"Skipped duplicate {match_id}")

            time.sleep(0.1)  # soft rate control

    db.close()


if __name__ == "__main__":
    run()
