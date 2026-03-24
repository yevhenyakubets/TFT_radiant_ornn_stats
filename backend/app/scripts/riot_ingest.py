import os
import time
import requests
import argparse
from app.services.patch_service import (
    get_current_patch,
    PATCH_SCHEDULE,
    get_patch_for_timestamp,
)


from dotenv import load_dotenv
from sqlalchemy.orm import Session
from pathlib import Path

from app.database import SessionLocal
from app.models.match import Match
from app.models.champion import Champion
from app.models.traits import Trait

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env", override=True)


MAX_INSERTS_PER_RUN = 100

PLATFORM_URL = "https://euw1.api.riotgames.com"
REGIONAL_URL = "https://europe.api.riotgames.com"


def get_existing_match_ids(db):
    rows = db.query(Match.match_id).all()
    return set(r[0] for r in rows)


def riot_get(url, params=None):
    headers = {"X-Riot-Token": os.getenv("RIOT_API_KEY")}
    while True:
        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            print(f"Rate limited. Sleeping {retry_after}s")
            time.sleep(retry_after)
            continue

        response.raise_for_status()
        return response.json()



def get_puuids_by_tier(tier: str, division: str | None):
    if tier in ["challenger", "grandmaster", "master"]:
        url = f"{PLATFORM_URL}/tft/league/v1/{tier}"
        data = riot_get(url)
        return [entry["puuid"] for entry in data.get("entries", [])]
    else:
        puuids = []
        page = 1
        while True:
            url = f"{PLATFORM_URL}/tft/league/v1/entries/{tier.upper()}/{division}"
            params = {"page": page}

            data = riot_get(url, params=params)

            if not data:
                break

            if isinstance(data, list):
                puuids.extend([entry["puuid"] for entry in data])
                print(f"Fetched page {page} - {len(data)} players")
            else:
                print(f"Unexpected response format on page {page}: {data}")
                break

            page += 1
            time.sleep(0.05)

        return puuids




def get_match_ids(puuid, start_time=None, count=20):
    url = f"{REGIONAL_URL}/tft/match/v1/matches/by-puuid/{puuid}/ids"
    params = {"start": 0, "count": count}
    if start_time:
        params["start_time"] = int(start_time)
    return riot_get(url, params=params)


def get_match(match_id):
    url = f"{REGIONAL_URL}/tft/match/v1/matches/{match_id}"
    return riot_get(url)



def insert_match(db: Session, match_id: str, data: dict):
    existing = db.query(Match).filter(Match.match_id == match_id).first()
    if existing:
        return False

    match = Match(match_id=match_id, data=data)
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
            "platinum",
        ],
        help="Rank tier to ingest",
    )

    parser.add_argument(
        "--division",
        choices=["I", "II", "III", "IV"],
        help="Division (required for diamond/emerald/platinum)",
    )

    return parser.parse_args()



def run():
    db = SessionLocal()

    current_patch_name = get_current_patch()
    patch_start_dt = PATCH_SCHEDULE.get(current_patch_name)
    start_time_epoch = int(patch_start_dt.timestamp()) if patch_start_dt else None

    print(f"Targeting Patch: {current_patch_name} (Starting {patch_start_dt})")

    total_inserted = 0
    existing_match_ids = get_existing_match_ids(db)
    args = parse_args()


    puuids = get_puuids_by_tier(args.tier, args.division)

    for puuid in puuids:
        match_ids = get_match_ids(puuid, start_time=start_time_epoch)

        for match_id in match_ids:
            if match_id in existing_match_ids:
                continue

            match_data = get_match(match_id)

            game_ms = match_data.get("info", {}).get("game_datetime")
            match_patch = get_patch_for_timestamp(game_ms)

            if match_patch != current_patch_name:
                print(
                    f"Reached end of patch for player (Match {match_id} is {match_patch}). Moving to next player."
                )
                break

            inserted = insert_match(db, match_id, match_data)
            if inserted:
                total_inserted += 1
                print(
                    f"Inserted {match_id} (Patch {match_patch}) [{total_inserted}/{MAX_INSERTS_PER_RUN}]"
                )
                existing_match_ids.add(match_id)

                if total_inserted >= MAX_INSERTS_PER_RUN:
                    print(f"Reached insert cap of {MAX_INSERTS_PER_RUN}. Stopping.")
                    db.close()
                    return

            time.sleep(0.05)

    db.close()


if __name__ == "__main__":
    run()
