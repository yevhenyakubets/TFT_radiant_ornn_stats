import requests
import sys
import os
import argparse
from sqlalchemy import text, inspect

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

def get_changes(obj):
    """
    Helper to detect which columns changed on a SQLAlchemy object.
    Returns a string of changes or None.
    """
    inspected = inspect(obj)
    changes = []
    for attr in inspected.mapper.column_attrs:
        history = inspected.get_history(attr.key, True)
        if history.has_changes():
            old_val = history.deleted[0] if history.deleted else "None"
            new_val = getattr(obj, attr.key)
            changes.append(f"{attr.key}: {old_val} -> {new_val}")
    return ", ".join(changes) if changes else None

def clear_data(db):
    """
    Wipes existing TFT data to allow for a fresh sync.
    Uses TRUNCATE CASCADE to restart identity sequences without dropping tables.
    """
    print("Cleaning database for a fresh start...")
    tables = [
        "champion_item_valid_pairs", "champion_roles", "item_roles",
        "champion_traits", "champions", "items", "traits", "roles"
    ]
    truncate_query = text(f"TRUNCATE {', '.join(tables)} RESTART IDENTITY CASCADE;")
    db.execute(truncate_query)
    db.commit()

def ingest_data(fresh_start=False):
    """
    Fetches raw TFT data from CommunityDragon and populates the local database.
    Processes Champions, Traits, Items, and generates Role-based Valid Pairs.
    """
    db = SessionLocal()
    current_set = get_current_set()
    url = "https://raw.communitydragon.org/pbe/cdragon/tft/en_us.json"
    
    if fresh_start:
        clear_data(db)
    
    try:
        print(f"Fetching data for Set {current_set}...")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        current_set_data = next(s for s in data['setData'] if s['number'] == current_set)

        old_pair_count = db.query(ChampionItemValidPairs).count()

        role_map = {}
        for r_name in ROLES_LIST:
            role = db.query(Role).filter_by(name=r_name).first()
            if not role:
                role = Role(name=r_name)
                db.add(role)
                db.flush()
                print(f"  [NEW] Role created: {r_name}")
            role_map[r_name] = role

        trait_map_by_name = {}
        for t_data in current_set_data.get('traits', []):
            rid = t_data['apiName']
            if not rid.startswith(f"TFT{current_set}_") or "Undetermined" in rid:
                continue
            
            name = (t_data.get('name') or "").strip()
            t_type = TRAIT_MAPPING.get(name, "Unique" if "Unique" in rid else "Unknown")
            
            trait = db.query(Trait).filter_by(riot_id=rid).first()
            is_new = False
            if not trait:
                trait = Trait(riot_id=rid)
                db.add(trait)
                is_new = True
            
            trait.name = name
            trait.type = t_type
            
            if is_new:
                print(f"  [NEW] Trait: {name}")
            else:
                changes = get_changes(trait)
                if changes: 
                    print(f"  [UPDATE] Trait {name}: {changes}")

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
            
            champ = db.query(Champion).filter_by(riot_id=rid).first()
            is_new = False
            if not champ:
                champ = Champion(riot_id=rid)
                db.add(champ)
                is_new = True

            champ.name = name
            champ.cost = c_data['cost']
            champ.ability_name = ability.get('name', "")
            champ.ability_desc = ability.get('desc', "")
            champ.ability_variables = {v['name']: v['value'] for v in ability.get('variables', [])}
            
            if is_new:
                print(f"  [NEW] Champion: {name}")
            else:
                changes = get_changes(champ)
                if changes: 
                    print(f"  [UPDATE] Champ {name}: {changes}")

            assigned_roles = CHAMPION_ROLE_MAPPING.get(name, [])
            champ.roles = [role_map[r] for r in assigned_roles if r in role_map]
            
            champ.traits = []
            for t_name in c_data.get('traits', []):
                if t_name in trait_map_by_name:
                    champ.traits.append(trait_map_by_name[t_name])

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

            item = db.query(Item).filter_by(riot_id=rid).first()
            is_new = False
            if not item:
                item = Item(riot_id=rid)
                db.add(item)
                is_new = True

            item.name = name
            item.type = i_type
            item.description = i_data.get('desc', "")
            item.effects = i_data.get('effects', {})
            
            if is_new:
                print(f"  [NEW] Item: {name}")
            else:
                changes = get_changes(item)
                if changes: 
                    print(f"  [UPDATE] Item {name}: {changes}")

            assigned_item_roles = ITEM_ROLE_MAPPING.get(name, [])
            item.roles = [role_map[r] for r in assigned_item_roles if r in role_map]
            
            db.flush()
            item_list.append(item)

        db.execute(text("TRUNCATE champion_item_valid_pairs RESTART IDENTITY;"))
        
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
        
        if old_pair_count != pairs_created:
            print(f"  [ROLES] Pairing logic recalculated: {old_pair_count} -> {pairs_created} pairs.")
            
        print(f"Sync Complete: {len(champ_list)} Champions, {len(item_list)} Items.")

    except Exception as e:
        db.rollback()
        print(f"FAILED TO SYNC: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync TFT data from CommunityDragon.")
    parser.add_argument("--fresh", action="store_true", help="Wipe all data before syncing.")
    args = parser.parse_args()
    
    ingest_data(fresh_start=args.fresh)