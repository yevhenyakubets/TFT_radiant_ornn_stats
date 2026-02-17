import requests
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.traits import Trait

# URL for the en_us convenience file
CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"

def sync_data():
    print("DEBUG: Entering sync_data function") # Add this
    db: Session = SessionLocal()
    print("Fetching data from Community Dragon...")
    response = requests.get(CDRAGON_URL)
    data = response.json()

    # 1. Sync Items (Radiants and Artifacts)
    print("Syncing Items...")
    for item_data in data.get("items", []):
        riot_id = item_data.get("apiName")
        
        # Check if this item exists in your 'items' table
        db_item = db.query(Item).filter(Item.riot_id == riot_id).first()
        
        if db_item:
            db_item.description = item_data.get("desc")
            db_item.effects = item_data.get("effects")
            print(f"  Updated Item: {db_item.name}")

    # 2. Sync Champions (Set 16 Units)
    print("Syncing Champions...")
    for unit_data in data.get("sets", {}).get("16", {}).get("champions", []):
        riot_id = unit_data.get("apiName")
        
        db_char = db.query(Champion).filter(Champion.riot_id == riot_id).first()
        
        if db_char:
            # TFT Abilities are nested under 'ability'
            # Inside your champion sync loop in cdragon_champions_ingest.py
            ability = unit_data.get("ability", {})
            db_char.ability_name = ability.get("name")
            db_char.ability_desc = ability.get("desc")

            # MERGE LOGIC: Capture variables AND calculations
            raw_vars = ability.get("variables", [])
            raw_calcs = ability.get("calculations", {})

            # We convert calculations into a format the parser can read
            # Calculations usually look like: {"scaleAP": {"asPercent": True, "value": [0, 50, 75, 100]}}
            merged_data = {
                "vars": raw_vars,
                "calculations": raw_calcs
            }

            db_char.ability_variables = merged_data

            print(f"  Updated Champion: {db_char.name}")

    db.commit()
    db.close()
    print("Sync Complete!")

if __name__ == "__main__":
    sync_data()