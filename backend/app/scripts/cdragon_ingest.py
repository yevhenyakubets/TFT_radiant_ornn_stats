import requests
import json
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.traits import Trait

CDRAGON_URL = "https://raw.communitydragon.org/latest/cdragon/tft/en_us.json"


def sync_data():
    db: Session = SessionLocal()
    print("Fetching latest patch data from Community Dragon...")
    response = requests.get(CDRAGON_URL)
    data = response.json()

    # 1. Sync Items
    print("\n--- Syncing Items ---")
    for item_data in data.get("items", []):
        riot_id = item_data.get("apiName")
        db_item = db.query(Item).filter(Item.riot_id == riot_id).first()

        if db_item:
            new_desc = item_data.get("desc")
            new_effects = item_data.get("effects")

            # Only update if the description or effects have changed
            if db_item.description != new_desc or db_item.effects != new_effects:
                db_item.description = new_desc
                db_item.effects = new_effects
                print(f"  [UPDATED] {db_item.name}")
            else:
                pass  # No change detected

    # 2. Sync Champions
    print("\n--- Syncing Champions ---")
    # Accessing Set 16 Champions
    champions_list = data.get("sets", {}).get("16", {}).get("champions", [])

    for unit_data in champions_list:
        riot_id = unit_data.get("apiName")
        db_char = db.query(Champion).filter(Champion.riot_id == riot_id).first()

        if db_char:
            ability = unit_data.get("ability", {})
            new_ability_name = ability.get("name")
            new_ability_desc = ability.get("desc")

            # Prepare the new merged data for comparison
            new_merged_data = {
                "vars": ability.get("variables", []),
                "calculations": ability.get("calculations", {}),
            }

            # Comparison Check
            # Note: Python dictionaries/lists comparison works deep-level here
            has_changes = (
                db_char.ability_name != new_ability_name
                or db_char.ability_desc != new_ability_desc
                or db_char.ability_variables != new_merged_data
            )

            if has_changes:
                db_char.ability_name = new_ability_name
                db_char.ability_desc = new_ability_desc
                db_char.ability_variables = new_merged_data
                print(f"  [UPDATED] {db_char.name}")
            else:
                pass  # Already up to date

    print("\nFinalizing changes...")
    db.commit()
    db.close()
    print("Sync Complete!")


if __name__ == "__main__":
    sync_data()
