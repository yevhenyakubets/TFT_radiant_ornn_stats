from sqlalchemy import text
from app.database import SessionLocal
from app.services.patch_service import get_current_patch, get_patch_for_timestamp
import json

def populate_champion_stats():
    db = SessionLocal()
    current_patch = get_current_patch()
    print(f"Current patch: {current_patch}, only processing matches from this patch.")

    try:
        total_count = db.execute(text("""
            SELECT COUNT(*) FROM matches
            WHERE processed = TRUE AND processed_champion_stats = FALSE
        """)).scalar()
        print(f"Found {total_count} unprocessed matches, processing in batches...")

        skipped = 0
        inserted = 0
        processed = 0
        batch_size = 100

        while True:
            matches = db.execute(text("""
                SELECT match_id, data FROM matches
                WHERE processed = TRUE AND processed_champion_stats = FALSE
                LIMIT :limit 
            """), {"limit": batch_size}).fetchall()

            if not matches:
                break

            for match_id, data in matches:
                raw = data if isinstance(data, dict) else json.loads(data)
                game_datetime = raw["info"]["game_datetime"]
                match_patch = get_patch_for_timestamp(game_datetime)

                if match_patch != current_patch:
                    skipped += 1
                else:
                    participants = raw["info"]["participants"]
                    for participant in participants:
                        placement = participant["placement"]
                        for unit in participant["units"]:
                            champion_id = unit["character_id"]
                            db.execute(text("""
                                INSERT INTO champion_stats (champion_id, match_id, patch, placement)
                                VALUES (:champion_id, :match_id, :patch, :placement)
                                ON CONFLICT (champion_id, match_id) DO NOTHING
                            """), {
                                "champion_id": champion_id,
                                "match_id": match_id,
                                "patch": match_patch,
                                "placement": placement
                            })
                            inserted += 1

                db.execute(text("""
                    UPDATE matches SET processed_champion_stats = TRUE
                    WHERE match_id = :match_id
                """), {"match_id": match_id})
                processed += 1

            db.commit()
            print(f"Processed {processed}/{total_count}...")

        print(f"Done. Inserted {inserted} rows, skipped {skipped} off-patch matches.")
    finally:
        db.close()

if __name__ == "__main__":
    populate_champion_stats()