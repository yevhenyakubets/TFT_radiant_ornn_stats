from sqlalchemy import delete, select
import json
from app.database import SessionLocal
from app.models.match import Match
from app.models.champion_stats import ChampionStat
from app.models.champion_item_stats import ChampionItemStats
from app.services.patch_service import get_current_patch, get_patch_for_timestamp

def cleanup_old_data():
    """
    Removes entries from matches, champion_stats, and champion_item_stats based on:
    1. Removes stats rows where patch is older than current.
    2. Removes matches where (patch is outdated) OR (both processed flags are true).
    """
    db = SessionLocal()
    current_patch = get_current_patch()
    CHUNK_SIZE = 500  # Prevents PostgreSQL parameter limit crashes
    print(f"Current patch: {current_patch}. Purging old or fully processed data...")

    try:
        deleted_cis = db.execute(
            delete(ChampionItemStats).where(ChampionItemStats.patch != current_patch)
        ).rowcount
        deleted_cs = db.execute(
            delete(ChampionStat).where(ChampionStat.patch != current_patch)
        ).rowcount
        print(f"Deleted {deleted_cis} old champion_item_stats and {deleted_cs} old champion_stats.")

        print("Evaluating matches for old patches or fully processed flags...")
        matches = db.execute(select(Match)).scalars().all()

        matches_to_delete = []
        for match in matches:
            if match.processed_item_stats and match.processed_champion_stats:
                matches_to_delete.append(match.match_id)
                continue
                
            raw = match.data if isinstance(match.data, dict) else json.loads(match.data)
            game_datetime = raw.get("info", {}).get("game_datetime")
            
            if game_datetime:
                match_patch = get_patch_for_timestamp(game_datetime)
                if match_patch != current_patch:
                    matches_to_delete.append(match.match_id)

        if matches_to_delete:
            total_matches = len(matches_to_delete)
            
            print(f"Purging cascading stats for {total_matches} matches in chunks...")
            for i in range(0, total_matches, CHUNK_SIZE):
                chunk = matches_to_delete[i:i + CHUNK_SIZE]
                db.execute(delete(ChampionItemStats).where(ChampionItemStats.match_id.in_(chunk)))
                db.execute(delete(ChampionStat).where(ChampionStat.match_id.in_(chunk)))
            
            print(f"Purging {total_matches} match records from disk in chunks...")
            total_deleted_matches = 0
            for i in range(0, total_matches, CHUNK_SIZE):
                chunk = matches_to_delete[i:i + CHUNK_SIZE]
                deleted_count = db.execute(delete(Match).where(Match.match_id.in_(chunk))).rowcount
                total_deleted_matches += deleted_count
                
            print(f"Successfully deleted {total_deleted_matches} match records.")
        else:
            print("No matches qualified for cleanup.")

        db.commit()
        print("Cleanup complete.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_old_data()