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


def render_description(desc, data_block):
    if not desc: return ""
    
    # 1. Clean HTML, spaces, and Riot-specific icons
    desc = re.sub(r'<[^>]*>', '', desc)
    desc = desc.replace('&nbsp;', ' ')
    
    # Replace scale icons with clean text tags
    desc = re.sub(r'%i:scaleAP%', '(AP)', desc)
    desc = re.sub(r'%i:scaleAD%', '(AD)', desc)
    desc = re.sub(r'%i:\w+%', '', desc)

    # 2. Extract stats into a simple dictionary
    stats = {v['name']: v['value'] for v in data_block.get("vars", [])}

    def replace_match(match):
        raw_token = match.group(1)
        multiplier = 1.0
        
        # Handle math inside the token (e.g., @Value*100@)
        token = raw_token
        if '*' in raw_token:
            token, factor = raw_token.split('*')
            multiplier = float(factor)

        # --- STEP 1: RESOLVE TOKEN ---
        # Try Direct Match -> Try "Modified" variant -> Try "Total" variant
        val = stats.get(token)
        if val is None:
            # If desc says @ModifiedDamage@, try finding @Damage@ or @ADDamage@
            for alt in [token.replace("Modified", ""), "AD" + token.replace("Modified", ""), "AP" + token.replace("Modified", "")]:
                if alt in stats:
                    val = stats[alt]
                    break
        
        # If we still haven't found it, check if it's a known mismatch (Teemo's PrimaryDamage)
        if val is None:
            if "Damage" in token and "PrimaryDamage" in stats: val = stats["PrimaryDamage"]
            elif "Heal" in token and "YuumiHeal" in stats: val = stats["YuumiHeal"]

        if val is None: return ""

        # --- STEP 2: APPLY MATH & FORMATTING ---
        if isinstance(val, list):
            raw_levels = [float(v) for v in val[1:4]]
            
            # Smart Multiplier Logic:
            # Only multiply by 100 if:
            # A) The token explicitly asked for it (*100)
            # B) It's an AttackSpeed token and the value is a small decimal (< 5)
            # C) It's an "AttackSpeed" token that ISN'T already a whole number (like Kobuko's 25)
            final_multiplier = multiplier
            if "AttackSpeed" in token or "AS" in token:
                if all(x < 5 for x in raw_levels) and multiplier == 1.0:
                    final_multiplier = 100.0

            levels = [round(x * final_multiplier) for x in raw_levels]
            
            # --- STEP 3: SUFFIXES ---
            suffix = ""
            if any(k in token for k in ["AttackSpeed", "AS", "Percent", "Reduction"]):
                suffix = "%"

            # Collapse single numbers: 4 / 4 / 4 -> 4
            if all(x == levels[0] for x in levels):
                return f"{levels[0]}{suffix}"
            
            return " / ".join(map(str, levels)) + suffix
        
        # Non-list value (singular numbers)
        return str(round(float(val) * multiplier))

    # Execute replacement
    final_desc = re.sub(r'@([^@]+)@', replace_match, desc)
    
    # Cleanup artifacts
    final_desc = final_desc.replace("((", "(").replace("))", ")")
    return re.sub(r'\s+', ' ', final_desc).strip()


def render_champion_description(desc, data_block):
    if not desc:
        return ""

    # 1. CLEAN HTML AND NON-BREAKING SPACES
    # Removes things like <spellPassive>, <TFTBonus>, and &nbsp;
    desc = re.sub(r'<[^>]*>', '', desc)
    desc = desc.replace('&nbsp;', ' ')

    # 2. PREPARE THE DATA MAP
    # We turn the vars list into a dictionary for O(1) lookup
    stats = {v['name']: v['value'] for v in data_block.get("vars", [])}

    # 3. ICON REPLACEMENT
    # Map Riot's icon codes to human-readable labels
    icon_map = {
        '%i:scaleAP%': 'AP',
        '%i:scaleAD%': 'AD',
        '%i:scaleAS%': 'AS',
        '%i:scaleHealth%': 'HP',
        '%i:scaleArmor%': 'Armor',
        '%i:scaleMR%': 'MR'
    }
    
    # We find all icon groups like (%i:scaleAD%%i:scaleAP%) and turn them into (AD, AP)
    def clean_icons(match):
        icons = re.findall(r'%i:scale\w+%', match.group(0))
        labels = [icon_map.get(i, i) for i in icons]
        return f"({', '.join(labels)})"

    desc = re.sub(r'\((%i:scale\w+%)+\)', clean_icons, desc)

    # 4. TOKEN REPLACEMENT LOGIC
    def replace_token(match):
        token = match.group(1)
        
        # Handle multipliers if present (e.g., @Value*100@)
        multiplier = 1.0
        if '*' in token:
            token, factor = token.split('*')
            multiplier = float(factor)

        # AGGREGATION LOGIC:
        # If the token is 'ModifiedSelfHeal', we look for components like 'SelfHealAP' + 'SelfHealHealthPercent'
        # If it's 'TotalDamage', we look for 'ADDamage' + 'APDamage'
        
        base_name = token.replace('Modified', '').replace('Total', '')
        
        # Find all keys in stats that relate to this token
        # e.g., for 'Heal', find 'YuumiHeal', 'AllyHealAP', etc.
        relevant_vals = []
        
        # Priority 1: Exact Match
        if token in stats:
            relevant_vals.append(stats[token])
        # Priority 2: Components (Aggregating HP + AP scaling)
        else:
            for key, val in stats.items():
                if base_name.lower() in key.lower():
                    # Avoid double counting if 'Modified' version exists
                    if "Modified" not in key or key == token:
                        relevant_vals.append(val)

        if not relevant_vals:
            return "???" # Fallback for truly missing data

        # Calculate values per star level (TFT star levels are indices 1, 2, 3)
        star_values = []
        for i in range(1, 4):
            total = sum(float(v[i]) if isinstance(v, list) else float(v) for v in relevant_vals)
            star_values.append(round(total * multiplier))

        # FORMATTING THE OUTPUT
        # Rule: If all star levels are the same, show one number (e.g., "3")
        if all(x == star_values[0] for x in star_values):
            return str(star_values[0])
        
        # Rule: Show as "140/180/240"
        return "/".join(map(str, star_values))

    # 5. EXECUTION
    final_desc = re.sub(r'@([^@]+)@', replace_token, desc)
    
    # Final cleanup of whitespace
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
    
    return rendered_desc, cleaned_effects