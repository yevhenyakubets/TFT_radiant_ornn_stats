import requests
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.champion import Champion
from app.models.traits import Trait

TRAITS_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tfttraits.json"
PLANNER_URL = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/tftchampions-teamplanner.json"

def sync_traits_and_connections():
    db: Session = SessionLocal()
    
    # 1. Sync Traits Table
    print("--- Phase 1: Syncing Traits ---")
    traits_data = requests.get(TRAITS_URL).json()
    
    for t_data in traits_data:
        # Match the "trait_id" field from your JSON example
        riot_id = t_data.get("trait_id") 
        
        if riot_id and ("TFT16_" in riot_id or "TFTSet16_" in riot_id):
            trait = db.query(Trait).filter(Trait.riot_id == riot_id).first()
            if not trait:
                trait = Trait(riot_id=riot_id)
                db.add(trait)
            
            # Using the exact fields from your snippet
            trait.name = t_data.get("display_name")
            trait.description = t_data.get("tooltip_text")
            # Store all innate and conditional sets as JSON
            trait.effects = {
                "innate": t_data.get("innate_trait_sets"),
                "conditional": t_data.get("conditional_trait_sets")
            }
            print(f"  Synced Trait: {trait.name} ({riot_id})")

    db.commit()

    # 2. Sync Champion-Trait Relationships
    print("\n--- Phase 2: Linking Champions ---")
    planner_json = requests.get(PLANNER_URL).json()
    set_16_units = planner_json.get("TFTSet16", [])

    for unit in set_16_units:
        # Match the "character_id" field from your planner snippet
        char_riot_id = unit.get("character_id") 
        
        db_char = db.query(Champion).filter(Champion.riot_id == char_riot_id).first()
        
        if db_char:
            db_char.traits = [] # Reset existing
            
            # In your snippet, traits is a list of objects: [{"name": "...", "id": "..."}]
            trait_list = unit.get("traits", [])
            for trait_obj in trait_list:
                t_riot_id = trait_obj.get("id")
                
                # Link to the trait we just saved in Phase 1
                trait = db.query(Trait).filter(Trait.riot_id == t_riot_id).first()
                if trait:
                    db_char.traits.append(trait)
                    print(f"  Linked {db_char.name} -> {trait.name}")
        else:
            # This helps you see if your DB has 'Aatrox' but the JSON has 'TFT16_Aatrox'
            print(f"  [SKIPPED] Champion {char_riot_id} not found in your database.")

    db.commit()
    db.close()
    print("\nSync Complete!")

if __name__ == "__main__":
    sync_traits_and_connections()