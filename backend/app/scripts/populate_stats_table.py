from datetime import datetime, UTC, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import SessionLocal
from app.models.match import Match
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion import Champion
from app.models.items import Item


PATCH_SCHEDULE = {
    "16.2": datetime(2026, 1, 8, tzinfo=timezone.utc),
    "16.3": datetime(2026, 1, 22, tzinfo=timezone.utc),
    "16.4": datetime(2026, 2, 4, tzinfo=timezone.utc),
    "16.5": datetime(2026, 2, 19, tzinfo=timezone.utc),
    "16.6": datetime(2026, 3, 4, tzinfo=timezone.utc),
    "16.7": datetime(2026, 3, 18, tzinfo=timezone.utc),
    "16.8": datetime(2026, 4, 1, tzinfo=timezone.utc),
    "17.1": datetime(2026, 4, 15, tzinfo=timezone.utc),
    "17.2": datetime(2026, 4, 29, tzinfo=timezone.utc),
    "17.3": datetime(2026, 5, 13, tzinfo=timezone.utc),
    "17.4": datetime(2026, 5, 28, tzinfo=timezone.utc),
    "17.5": datetime(2026, 6, 10, tzinfo=timezone.utc),
    "17.6": datetime(2026, 6, 24, tzinfo=timezone.utc),
    "17.7": datetime(2026, 7, 15, tzinfo=timezone.utc),
    "18.1": datetime(2026, 7, 29, tzinfo=timezone.utc),
    "18.2": datetime(2026, 8, 12, tzinfo=timezone.utc),
    "18.3": datetime(2026, 8, 26, tzinfo=timezone.utc),
    "18.4": datetime(2026, 9, 10, tzinfo=timezone.utc),
    "18.5": datetime(2026, 9, 23, tzinfo=timezone.utc),
    "18.6": datetime(2026, 10, 7, tzinfo=timezone.utc),
    "18.7": datetime(2026, 10, 21, tzinfo=timezone.utc),
    "18.8": datetime(2026, 11, 4, tzinfo=timezone.utc),
    "19.1": datetime(2026, 11, 18, tzinfo=timezone.utc),
    "19.2": datetime(2026, 12, 7, tzinfo=timezone.utc),
}

def get_current_patch():
    now = datetime.now(timezone.utc)

    sorted_patches = sorted(
        PATCH_SCHEDULE.items(),
        key=lambda x: x[1]
    )

    current_patch = None

    for patch, start_date in sorted_patches:
        if now >= start_date:
            current_patch = patch
        else:
            break

    return current_patch


def get_patch_for_timestamp(timestamp_ms: int):

    match_date = datetime.fromtimestamp(timestamp_ms / 1000, timezone.utc)

    sorted_patches = sorted(
        PATCH_SCHEDULE.items(),
        key=lambda x: x[1]
    )

    current_patch = None

    for patch, start_date in sorted_patches:
        if match_date >= start_date:
            current_patch = patch
        else:
            break

    return current_patch

def run():

    db: Session = SessionLocal()

    try:

        target_patch = get_current_patch()
        print(f"Current scheduled patch: {target_patch}")

        matches = db.execute(
            select(Match).where(Match.processed == False)
        ).scalars().all()

        champion_map = {
            c.riot_id: c.id
            for c in db.execute(select(Champion)).scalars().all()
        }

        item_map = {
            i.riot_id: i.id
            for i in db.execute(select(Item)).scalars().all()
        }

        total_inserted = 0
        total_processed = 0

        for match in matches:

            match_json = match.data
            info = match_json.get("info", {})

            timestamp = info.get("gameCreation")

            if not timestamp:
                continue

            normalized_patch = get_patch_for_timestamp(timestamp)

            # Only process matches from CURRENT patch
            if normalized_patch != target_patch:
                continue

            participants = info.get("participants", [])

            for player in participants:

                placement = player.get("placement")
                units = player.get("units", [])

                for unit in units:

                    champion_riot_id = unit.get("character_id")
                    item_names = unit.get("itemNames", [])

                    if champion_riot_id not in champion_map:
                        continue

                    champion_id = champion_map[champion_riot_id]

                    for item_riot_id in item_names:

                        if item_riot_id not in item_map:
                            continue

                        item_id = item_map[item_riot_id]

                        stat = ChampionItemStats(
                            match_id=match.match_id,
                            champion_id=champion_id,
                            item_id=item_id,
                            placement=placement,
                            normalized_patch=normalized_patch
                        )

                        db.add(stat)
                        total_inserted += 1

            match.processed = True
            total_processed += 1

        db.commit()

        print(f"Processed matches: {total_processed}")
        print(f"Inserted rows: {total_inserted}")
        print("Done.")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    run()
