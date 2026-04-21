import json
from sqlalchemy import select
from app.database import SessionLocal
from app.models.match import Match
from app.models.champion import Champion
from app.models.champion_stats import ChampionStat
from app.services.patch_service import get_current_patch, get_patch_for_timestamp

def populate_champion_stats():
    """
    Populates the champion_stats table in the db by processing raw match jsons in matches table.
    Looks for matches where processed_champion_stats flag is equal to False AND processed_item_stats flag is equal to True, 
    then flags all processed matches as True(if script finishes running succesfully).
    """
    db = SessionLocal()
    current_patch = get_current_patch()
    print(f"Current patch: {current_patch}. Filtering for relevant match data.")

    

    try:
        stmt = select(Match).where(
            Match.processed_item_stats, 
            ~Match.processed_champion_stats
        )
        matches = db.execute(stmt).scalars().all()
        
        total_count = len(matches)
        print(f"Found {total_count} matches requiring champion stat extraction.")

        skipped = 0
        inserted = 0
        processed_count = 0

        champion_map = {
            c.riot_id: c.id for c in db.execute(select(Champion)).scalars().all()
        }

        for match in matches:
            raw = match.data if isinstance(match.data, dict) else json.loads(match.data)
            game_datetime = raw["info"]["game_datetime"]
            match_patch = get_patch_for_timestamp(game_datetime)

            if match_patch != current_patch:
                skipped += 1
            else:
                participants = raw["info"]["participants"]
                for participant in participants:
                    placement = participant["placement"]
                    puuid = participant["puuid"]
                    
                    for unit in participant["units"]:
                        riot_id = unit["character_id"]
                        champ_db_id = champion_map.get(riot_id)

                        if champ_db_id is None:
                            continue

                        stat_entry = ChampionStat(
                            champion_id=champ_db_id,
                            match_id=match.match_id,
                            puuid=puuid,
                            patch=match_patch,
                            placement=placement
                        )
                        db.merge(stat_entry)
                        inserted += 1

            match.processed_champion_stats = True
            processed_count += 1

            if processed_count % 100 == 0:
                db.commit()
                print(f"Progress: {processed_count}/{total_count}...")

        db.commit()
        print(f"Done. Inserted {inserted} champion rows, skipped {skipped} off-patch matches.")
    
    except Exception as e:
        db.rollback()
        print(f"Error during champion stat population: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    populate_champion_stats()