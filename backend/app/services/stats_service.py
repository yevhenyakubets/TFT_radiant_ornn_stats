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
    
    readable_ability = render_champion_description(
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
    
    readable_desc = render_item_data(item.description, item.effects)
    
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

    readable_desc = render_item_data(item.description, item.effects)

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

import re

def render_champion_description(desc, data_block):
    if not desc:
        return ""

    # 1. CLEANING
    desc = re.sub(r'<[^>]*>', '', desc)
    desc = desc.replace('&nbsp;', ' ')

    # 2. DATA PREP
    stats = {v['name'].lower(): v['value'] for v in data_block.get("vars", [])}

    # 3. THE EXCEPTION MAP (Simplified Syntax)
    # Format: "token": ([List of variables to sum], multiplier_variable)
    EXCEPTIONS = {
        "modifiedaciddamage": (["addamage", "apdamage"], "acidpercentdamage"),
        "totaldamage": (["addamage", "apdamage"], None)
    }
    def format_star_values(vals):
        if not vals: return "???"
        if all(x == vals[0] for x in vals):
            return str(vals[0])
        # Only hide the 3rd value if it is exactly 0 and the 1st value is not
        if len(vals) >= 3 and vals[2] == 0 and vals[0] != 0:
            # Check if index 2 was actually 0 or just rounded to 0
            return f"{vals[0]}/{vals[1]}"
        return "/".join(map(str, [str(v).rstrip('0').rstrip('.') for v in vals]))

    # 5. ICON REPLACEMENT
    icon_map = {
        '%i:scaleap%': 'AP', '%i:scalead%': 'AD', '%i:scaleas%': 'AS',
        '%i:scalehealth%': 'HP', '%i:scalearmor%': 'Armor', '%i:scalemr%': 'MR'
    }
    
    def clean_icons(match):
        found = re.findall(r'%i:scale\w+%', match.group(0).lower())
        if not found: return ""
        labels = [icon_map.get(i, i.replace('%i:scale', '').replace('%', '')) for i in found]
        return f"({', '.join(labels)})"

    desc = re.sub(r'\((%i:scale\w+%)+\)', clean_icons, desc, flags=re.IGNORECASE)

    # 6. TOKEN REPLACEMENT
    def replace_token(match):
        raw_token = match.group(1)
        multiplier = 1.0
        
        token_name = raw_token
        if '*' in raw_token:
            token_name, factor = raw_token.split('*')
            multiplier = float(factor)
        
        token_lower = token_name.lower()

        # --- STEP A: Check Exception Map ---
        if token_lower in EXCEPTIONS:
            sum_keys, mult_key = EXCEPTIONS[token_lower]
            star_values = []
            
            for i in range(1, 4):
                base_sum = 0
                for key in sum_keys:
                    val_list = stats.get(key, [0]*7)
                    base_sum += float(val_list[i] if i < len(val_list) else 0)
                
                if mult_key:
                    mult_list = stats.get(mult_key, [1]*7)
                    mult_val = float(mult_list[i] if i < len(mult_list) else 1)
                    final = base_sum * mult_val * multiplier
                else:
                    final = base_sum * multiplier
                
                # Decimal-aware rounding for time-based tokens
                if any(word in token_lower for word in ["seconds", "duration"]):
                    star_values.append(round(final, 2))
                else:
                    star_values.append(round(final))
            return format_star_values(star_values)

        # --- STEP B: Standard Aggregation ---
        base_name = token_lower.replace('modified', '').replace('total', '')
        relevant_vals = []
        
        if token_lower in stats:
            relevant_vals.append(stats[token_lower])
        else:
            for key, val in stats.items():
                if base_name in key:
                    if "modified" not in key or key == token_lower:
                        relevant_vals.append(val)

        if not relevant_vals:
            return "???"

        star_values = []
        for i in range(1, 4):
            current_sum = 0
            for v in relevant_vals:
                try:
                    val = v[i] if isinstance(v, list) else v
                    if val is not None: current_sum += float(val)
                except: continue
            
            final = current_sum * multiplier
            
            # Auto-fix 0.4 -> 40 for percentage-based names
            if ("percent" in token_lower or "ratio" in token_lower) and 0 < final < 2:
                final *= 100
            
            # Decimal-aware rounding for time-based tokens
            if any(word in token_lower for word in ["seconds", "duration"]):
                star_values.append(round(final, 2))
            else:
                star_values.append(round(final))

        return format_star_values(star_values)

    # 7. EXECUTION
    final_desc = re.sub(r'@([^@]+)@', replace_token, desc)
    return re.sub(r'\s+', ' ', final_desc).strip()

def render_item_data(desc, effects_raw):
    """
    Processes item descriptions and effects.
    Returns a tuple: (rendered_description, cleaned_effects)
    """
    if not desc:
        return "", effects_raw

    # 1. CLEAN HTML AND ITEM RULE TAGS
    # Removes <tftitemrules>, <TFTTrackerLabel>, etc.
    desc = re.sub(r'<[^>]*>', '', desc)
    desc = desc.replace('&nbsp;', ' ')
    
    # Clean up specific gold icons or currency symbols
    desc = desc.replace('%i:goldCoins%', '')

    # 2. RENDER DESCRIPTION
    def replace_item_token(match):
        token = match.group(1)
        
        # Handle Riot's Tracker/Property tokens (e.g., @TFTUnitProperty.item... @)
        # These are usually 0 for a fresh item description.
        if "TFTUnitProperty" in token:
            return "0"

        # Handle math multipliers (e.g., @AD*100@)
        multiplier = 1.0
        if '*' in token:
            token, factor = token.split('*')
            multiplier = float(factor)

        # Lookup in effects
        val = effects_raw.get(token)
        
        if val is None:
            return "???"

        # Items use single floats/ints. 
        # If it's a small decimal (like 0.25 for AD), and the token isn't asking for *100,
        # we check if it's meant to be a percentage.
        num = float(val)
        
        # Most item variables in the JSON are already whole numbers (50, 4, 12)
        # except for AD/AP/Omnivamp which are often 0.25 (25%)
        return str(round(num * multiplier))

    rendered_desc = re.sub(r'@([^@]+)@', replace_item_token, desc)
    
    # 3. CLEAN UP EFFECTS FOR FRONTEND
    # This creates a pretty version of the stats for your UI
    cleaned_effects = {}
    for key, val in effects_raw.items():
        # Only include stats that are actually numbers
        if isinstance(val, (int, float)):
            # Convert 0.25 to 25 for stats like AD/Omnivamp
            if 0 < val < 1:
                cleaned_effects[key] = round(val * 100)
            else:
                cleaned_effects[key] = round(val)

    # Final whitespace cleanup
    rendered_desc = re.sub(r'\s+', ' ', rendered_desc).strip()
    
    return rendered_desc