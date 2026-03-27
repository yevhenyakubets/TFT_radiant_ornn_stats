from datetime import datetime, UTC, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database import SessionLocal
from app.models.match import Match
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion import Champion
from app.models.items import Item
from app.models.traits import Trait
from app.services.patch_service import get_current_patch, get_patch_for_timestamp

def run():

    db: Session = SessionLocal()

    try:
        target_patch = get_current_patch()
        print(f"Current scheduled patch: {target_patch}")

        matches = (
            db.execute(select(Match).where(not Match.processed)).scalars().all()
        )

        champion_map = {
            c.riot_id: c.id for c in db.execute(select(Champion)).scalars().all()
        }

        item_map = {i.riot_id: i.id for i in db.execute(select(Item)).scalars().all()}

        total_inserted = 0
        total_processed = 0

        for match in matches:
            match_json = match.data
            info = match_json.get("info", {})

            timestamp = info.get("gameCreation")

            if not timestamp:
                continue

            normalized_patch = get_patch_for_timestamp(timestamp)

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
                            normalized_patch=normalized_patch,
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
