from sqlalchemy import delete, select
import json
from app.database import SessionLocal
from app.models.match import Match
from app.models.champion_stats import ChampionStat
from app.models.champion_item_stats import ChampionItemStats
from app.services.patch_service import get_current_patch, get_patch_for_timestamp

def cleanup_old_data():
    """
    Removes all entries from matches, champion_stats, and champion_item_stats
    tables of the DB where patch is older than current
    """
    db = SessionLocal()
    current_patch = get_current_patch()
    print(f"Current patch: {current_patch}. Purging all data from previous patches...")

    try:
        deleted_cis = db.execute(
            delete(ChampionItemStats).where(ChampionItemStats.patch != current_patch)
        ).rowcount
        deleted_cs = db.execute(
            delete(ChampionStat).where(ChampionStat.patch != current_patch)
        ).rowcount
        print(f"Deleted {deleted_cis} old champion_item_stats and {deleted_cs} old champion_stats.")

        print("Evaluating match patches...")
        matches = db.execute(select(Match)).scalars().all()

        matches_to_delete = []
        for match in matches:
            raw = match.data if isinstance(match.data, dict) else json.loads(match.data)
            game_datetime = raw.get("info", {}).get("game_datetime")
            
            if game_datetime:
                match_patch = get_patch_for_timestamp(game_datetime)
                if match_patch != current_patch:
                    matches_to_delete.append(match.match_id)

        if matches_to_delete:
            db.execute(
                delete(ChampionItemStats).where(ChampionItemStats.match_id.in_(matches_to_delete))
            )
            db.execute(
                delete(ChampionStat).where(ChampionStat.match_id.in_(matches_to_delete))
            )
            
            db.execute(
                delete(Match).where(Match.match_id.in_(matches_to_delete))
            )
            print(f"Deleted {len(matches_to_delete)} old match records.")
        else:
            print("No old matches found.")

        db.commit()
        print("Cleanup complete.")
        
    except Exception as e:
        db.rollback()
        print(f"Error during cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_old_data()