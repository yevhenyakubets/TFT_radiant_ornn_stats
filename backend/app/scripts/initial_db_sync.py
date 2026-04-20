import requests
import sys
import os
from sqlalchemy import text

# Ensures the script can find the 'app' module when run from the scripts folder.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.services.patch_service import get_current_set
from app.models.champion import Champion
from app.models.traits import Trait
from app.models.items import Item
from app.models.roles import Role
from app.models.champion_item_valid_pairs import ChampionItemValidPairs

from app.constants.set_config import (
    ARTIFACTS, 
    TRAIT_MAPPING, 
    CHAMPION_ROLE_MAPPING, 
    ITEM_ROLE_MAPPING, 
    ROLES_LIST
)

def clear_data(db):
    """
    Wipes existing TFT data to allow for a fresh sync.
    Uses TRUNCATE CASCADE to restart identity sequences without dropping tables.
    """
    print("Cleaning database...")
    tables = [
        "champion_item_valid_pairs", "champion_roles", "item_roles",
        "champion_traits", "champions", "items", "traits", "roles"
    ]
    truncate_query = text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE;")
    db.execute(truncate_query)
    db.commit()

def ingest_data():
    """
    Fetches raw TFT data from CommunityDragon and populates the local database.
    Processes Champions, Traits, Items, and generates Role-based Valid Pairs.
    """
    db = SessionLocal()
    current_set = get_current_set()
    url = "https://raw.communitydragon.org/pbe/cdragon/tft/en_us.json"
    
    clear_data(db)
    
    try:
        print(f"Fetching data for Set {current_set}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_set_data = next(s for s in data['setData'] if s['number'] == current_set)

        role_map = {}
        for r_name in ROLES_LIST:
            role = Role(name=r_name)
            db.add(role)
            db.flush()
            role_map[r_name] = role

        trait_map_by_name = {}
        for t_data in current_set_data.get('traits', []):
            rid = t_data['apiName']
            if not rid.startswith(f"TFT{current_set}_") or "Undetermined" in rid:
                continue
            
            name = (t_data.get('name') or "").strip()
            t_type = TRAIT_MAPPING.get(name, "Unique" if "Unique" in rid else "Unknown")
            
            trait = Trait(riot_id=rid, name=name, type=t_type)
            db.add(trait)
            db.flush()
            trait_map_by_name[name] = trait

        champ_list = []
        for c_data in current_set_data.get('champions', []):
            rid = c_data.get('apiName', "")
            name = (c_data.get('name') or "").strip()
            
            if not name or not rid or not rid.startswith(f"TFT{current_set}_") or not c_data.get('traits'):
                continue
            
            if any(x in rid for x in ["FakeUnit", "Pet", "Tether", "Mech"]):
                continue

            ability = c_data.get('ability', {})
            champ = Champion(
                riot_id=rid, name=name, cost=c_data['cost'],
                ability_name=ability.get('name', ""),
                ability_desc=ability.get('desc', ""),
                ability_variables={v['name']: v['value'] for v in ability.get('variables', [])}
            )
            
            assigned_roles = CHAMPION_ROLE_MAPPING.get(name, [])
            champ.roles = [role_map[r] for r in assigned_roles if r in role_map]
            
            for t_name in c_data.get('traits', []):
                if t_name in trait_map_by_name:
                    champ.traits.append(trait_map_by_name[t_name])

            db.add(champ)
            db.flush()
            champ_list.append(champ)

        item_list = []
        for i_data in data.get('items', []):
            rid = i_data.get('apiName', "")
            name = (i_data.get('name') or "").strip()
            
            if not name or not rid: 
                continue

            i_type = None
            if rid in ARTIFACTS:
                i_type = "artifact"
            elif rid.lower().startswith("tft5_") and name.lower().startswith("radiant"):
                if "spatula" not in rid.lower() and "emblem" not in rid.lower():
                    i_type = "radiant"
            
            if not i_type: 
                continue

            item = Item(
                riot_id=rid, name=name, type=i_type,
                description=i_data.get('desc', ""),
                effects=i_data.get('effects', {})
            )
            
            assigned_item_roles = ITEM_ROLE_MAPPING.get(name, [])
            item.roles = [role_map[r] for r in assigned_item_roles if r in role_map]
            
            db.add(item)
            db.flush()
            item_list.append(item)

        # Logic: If a Champion and Item share at least one Role, they are a valid pair.
        pairs_created = 0
        for champ in champ_list:
            c_role_ids = {r.id for r in champ.roles}
            if not c_role_ids: 
                continue
            
            for item in item_list:
                i_role_ids = {r.id for r in item.roles}
                if c_role_ids.intersection(i_role_ids):
                    pair = ChampionItemValidPairs(champion_id=champ.id, item_id=item.id)
                    db.add(pair)
                    pairs_created += 1
        
        db.commit()
        print(f"Sync Complete: {len(champ_list)} Champions, {len(item_list)} Items, {pairs_created} Pairs.")

    except Exception as e:
        db.rollback()
        print(f"FAILED TO SYNC: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()