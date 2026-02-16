from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
import re

from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion_item_valid_pairs import ChampionItemValidPairs


CURRENT_PATCH = "16.4"


# ================================
# INTERNAL QUERY HELPERS
# ================================

def _aggregate_stats(db: Session):
    """
    Returns aggregated stats:
    champion_id, item_id, count, avg_placement
    """

    results = (
        db.query(
            ChampionItemStats.champion_id,
            ChampionItemStats.item_id,
            func.count().label("count"),
            func.avg(ChampionItemStats.placement).label("avg_placement"),
        )
        .filter(ChampionItemStats.normalized_patch == CURRENT_PATCH)
        .group_by(
            ChampionItemStats.champion_id,
            ChampionItemStats.item_id,
        )
        .all()
    )

    return results


# ================================
# CHAMPION PAGE
# ================================

def get_champion_special_items(champion_riot_id: str):
    db = SessionLocal()

    champion = (
        db.query(Champion)
        .filter(Champion.riot_id == champion_riot_id)
        .first()
    )

    if not champion:
        db.close()
        return None
    
    readable_ability = render_description(
        champion.ability_desc, 
        champion.ability_variables
    )

    # total games for this champion in patch
    total_games = (
        db.query(func.count())
        .filter(
            ChampionItemStats.champion_id == champion.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .scalar()
    )

    stats = (
        db.query(
            ChampionItemStats.item_id,
            func.count().label("count"),
            func.avg(ChampionItemStats.placement).label("avg_placement"),
        )
        .filter(
            ChampionItemStats.champion_id == champion.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .group_by(ChampionItemStats.item_id)
        .all()
    )

    artifacts = {}
    radiants = {}

    for item_id, count, avg in stats:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            continue

        # VALID CHECK
        valid_pair = db.query(
            db.query(ChampionItemValidPairs)
            .filter(
                ChampionItemValidPairs.champion_id == champion.id,
                ChampionItemValidPairs.item_id == item.id,
            )
            .exists()
        ).scalar()

        # LOW SAMPLE CHECK
        percentage = count / total_games if total_games else 0
        low_sample = percentage < 0.05

        data = {
            "name": item.name,
            "count": count,
            "average_placement": float(avg),
            "type": item.type,
            "valid": bool(valid_pair),
            "low_sample": low_sample,
        }

        if item.type == "artifact":
            artifacts[item.riot_id] = data
        elif item.type == "radiant":
            radiants[item.riot_id] = data

    db.close()

    artifacts = dict(
        sorted(artifacts.items(), key=lambda x: x[1]["average_placement"])
    )
    radiants = dict(
        sorted(radiants.items(), key=lambda x: x[1]["average_placement"])
    )

    return {
        "champion": champion.riot_id,
        "name": champion.name,
        "cost": champion.cost,
        "ability_name": champion.ability_name,
        "ability_description": readable_ability,
        "artifacts": artifacts,
        "radiants": radiants,
    }



# ================================
# ARTIFACT PAGE
# ================================

def get_artifact_stats_by_id(artifact_riot_id: str):
    db = SessionLocal()

    item = (
        db.query(Item)
        .filter(Item.riot_id == artifact_riot_id, Item.type == "artifact")
        .first()
    )

    if not item:
        db.close()
        return None
    
    readable_desc = render_description(item.description, item.effects)
    
    # total games for this item
    total_games = (
        db.query(func.count())
        .filter(
            ChampionItemStats.item_id == item.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .scalar()
    )    

    stats = (
        db.query(
            ChampionItemStats.champion_id,
            func.count().label("count"),
            func.avg(ChampionItemStats.placement).label("avg_placement"),
        )
        .filter(
            ChampionItemStats.item_id == item.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .group_by(ChampionItemStats.champion_id)
        .all()
    )

    result = {}

    for champion_id, count, avg in stats:
        champion = db.query(Champion).filter(Champion.id == champion_id).first()
        if not champion:
            continue

        

        valid_pair = db.query(
            db.query(ChampionItemValidPairs)
            .filter(
                ChampionItemValidPairs.champion_id == champion.id,
                ChampionItemValidPairs.item_id == item.id,
            )
            .exists()
        ).scalar()

        percentage = count / total_games if total_games else 0
        low_sample = percentage < 0.02        

        result[champion.riot_id] = {
            "name": champion.name,
            "count": count,
            "average_placement": float(avg),
            "valid": bool(valid_pair),
            "low_sample": low_sample,
        }

    db.close()

    sorted_result = dict(
        sorted(result.items(), key=lambda x: x[1]["average_placement"])
    )

    return {
        "id": artifact_riot_id,
        "name": item.name,
        "type": "artifact",
        "description": readable_desc, # NEW
        "stats": item.effects,        # NEW (for stat icons in UI)
        "champions": sorted_result,
    }


# ================================
# RADIANT PAGE
# ================================

def get_radiant_stats_by_id(radiant_riot_id: str):
    db = SessionLocal()

    item = (
        db.query(Item)
        .filter(Item.riot_id == radiant_riot_id, Item.type == "radiant")
        .first()
    )

    if not item:
        db.close()
        return None
        # total games for this item

    readable_desc = render_description(item.description, item.effects)

    total_games = (
        db.query(func.count())
        .filter(
            ChampionItemStats.item_id == item.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .scalar()
    )  

    stats = (
        db.query(
            ChampionItemStats.champion_id,
            func.count().label("count"),
            func.avg(ChampionItemStats.placement).label("avg_placement"),
        )
        .filter(
            ChampionItemStats.item_id == item.id,
            ChampionItemStats.normalized_patch == CURRENT_PATCH,
        )
        .group_by(ChampionItemStats.champion_id)
        .all()
    )

    result = {}

    for champion_id, count, avg in stats:
        champion = db.query(Champion).filter(Champion.id == champion_id).first()
        if not champion:
            continue

        valid_pair = db.query(
            db.query(ChampionItemValidPairs)
            .filter(
                ChampionItemValidPairs.champion_id == champion.id,
                ChampionItemValidPairs.item_id == item.id,
            )
            .exists()
        ).scalar()

        percentage = count / total_games if total_games else 0
        low_sample = percentage < 0.02  

        result[champion.riot_id] = {
            "name": champion.name,
            "count": count,
            "average_placement": float(avg),
            "valid": bool(valid_pair),
            "low_sample": low_sample,
        }

    db.close()

    sorted_result = dict(
        sorted(result.items(), key=lambda x: x[1]["average_placement"])
    )

    return {
        "id": radiant_riot_id,
        "name": item.name,
        "type": "radiant",
        "description": readable_desc, # NEW
        "stats": item.effects,        # NEW (for stat icons in UI)
        "champions": sorted_result,
    }


def render_description(desc, effects_list):
    if not desc: return ""
    
    # NEW: Remove HTML-like tags from CDragon
    desc = re.sub(r'<[^>]*>', '', desc)
    
    stats = {}
    if isinstance(effects_list, dict):
        stats = effects_list
    elif isinstance(effects_list, list):
        for var in effects_list:
            stats[var['name']] = var['value']

    def replace_match(match):
        token = match.group(1)
        multiplier = 1
        if '*' in token:
            token, mult_val = token.split('*')
            multiplier = float(mult_val)

        val = stats.get(token, "???")
        
        if isinstance(val, list):
            # Champion variables often have a dummy index at [0]
            # Use indices 1, 2, 3 for star levels
            return " / ".join([str(round(v * multiplier)) for v in val[1:4]])
        
        return str(round(val * multiplier)) if isinstance(val, (int, float)) else str(val)

    return re.sub(r'@([^@]+)@', replace_match, desc)