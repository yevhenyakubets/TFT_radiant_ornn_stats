from sqlalchemy import text
from app.database import SessionLocal
from app.services.patch_service import get_current_patch, get_patch_for_timestamp

def cleanup_old_data():
    db = SessionLocal()
    current_patch = get_current_patch()
    print(f"Current patch: {current_patch}, cleaning up old and processed data...")

    try:
        # --- Clean champion_item_stats (old patch only) ---
        deleted_cis = db.execute(text("""
            DELETE FROM champion_item_stats
            WHERE normalized_patch != :current_patch
        """), {"current_patch": current_patch}).rowcount
        print(f"Deleted {deleted_cis} champion_item_stats rows.")

        # --- Clean champion_stats (old patch only) ---
        deleted_cs = db.execute(text("""
            DELETE FROM champion_stats
            WHERE patch != :current_patch
        """), {"current_patch": current_patch}).rowcount
        print(f"Deleted {deleted_cs} champion_stats rows.")

        # --- Clean matches ---
        print("Fetching matches...")
        matches = db.execute(text("""
            SELECT match_id,
                   (data->'info'->>'game_datetime')::bigint as game_datetime,
                   processed,
                   processed_champion_stats
            FROM matches
        """)).fetchall()

        matches_to_delete = []
        for row in matches:
            match_patch = get_patch_for_timestamp(row.game_datetime)
            if match_patch != current_patch or (row.processed and row.processed_champion_stats):
                matches_to_delete.append(row.match_id)

        if matches_to_delete:
            db.execute(text("""
                DELETE FROM matches WHERE match_id = ANY(:ids)
            """), {"ids": matches_to_delete})
            print(f"Deleted {len(matches_to_delete)} matches.")
        else:
            print("No matches to delete.")

        db.commit()
        print("Cleanup complete.")
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_old_data()