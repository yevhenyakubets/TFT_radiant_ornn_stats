from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.traits import Trait

def migrate_trait_types():
    db = SessionLocal()
    
    # Logic Mapping
    mapping = {
        "unique": [
            "World Ender", "Star Forger", "Riftscourge", "Blacksmith", "Caretaker",
            "Dark Child", "Emperor", "Glutton", "Harvester", "Heroic",
            "Rune Mage", "The Boss", "Eternal", "Soulbound", "Ascendant", 
            "Assimilator", "Chainbreaker", "Immortal", "Huntress", "Chronokeeper", "Dragonborn",
        ],
        "duo": [
            "Huntress", "Chosen Wolves", "Joint Album", "Poison Pals", "Spin to Win", "Dragonguards", "Sentinels of Light", 
            "Timewinders",
        ],
        "class": [
            "Blademaster", "Bruiser", "Defender", "Disruptor", "Gunslinger", 
            "Invoker", "Juggernaut", "Longshot", "Quickstriker", "Slayer", 
            "Vanquisher", "Warden",  "Arcanist"
        ],
        "origin": [
            "Bilgewater", "Demacia", "Freljord", 
            "HexMech", "Ionia", "Ixtal", "Lunari", "Noxus", "Piltover", 
            "Shadow Isles", "Shurima", "Targon", "Void", "Yordle", "Zaun", "Darkin"
        ]
    }

    try:
        traits = db.query(Trait).all()
        for trait in traits:
            found = False
            for t_type, trait_list in mapping.items():
                if trait.name in trait_list:
                    trait.type = t_type
                    found = True
                    break
            
            # Fallback if a trait isn't in the list
            if not found:
                trait.type = "origin" 
                
        db.commit()
        print("Successfully updated trait types.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_trait_types()