from sqlalchemy.orm import Session
from sqlalchemy import func
from collections import defaultdict
import re

from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion_item_valid_pairs import ChampionItemValidPairs


CURRENT_PATCH = "16.5"

DECREASING_STATS = ["attacks", "mana", "requirement", "cooldown"]


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

def get_sorted_traits(traits):
    """
    Filters out 'duo' traits, then sorts: Unique > Origin > Class. 
    Alphabetical within the same type.
    """
    # 1. Filter out duo traits immediately
    filtered_traits = [t for t in traits if t.type != "duo"]
    
    # 2. Define priority weights for the remaining types
    priority = {"unique": 0, "origin": 1, "class": 2}
    
    # 3. Sort by priority first, then by name
    sorted_list = sorted(
        filtered_traits, 
        key=lambda t: (priority.get(t.type, 99), t.name)
    )
    
    return [
        {
            "name": t.name,
            "type": t.type,
            "riot_id": t.riot_id
        } 
        for t in sorted_list
    ]

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
    
    sorted_traits = get_sorted_traits(champion.traits)

    if not champion:
        db.close()
        return None
    
    readable_ability = render_champion_description(
        champion.ability_desc, 
        champion.ability_variables,
        champion.name
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
        low_sample = percentage < 0.02

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
        "traits": sorted_traits,
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
        low_sample = percentage < 0.01        

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
        low_sample = percentage < 0.01  

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

def render_champion_description(desc, data_block, champion_name):
    if not desc:
        return ""

    # 1. CLEANING
    desc = re.sub(r'<[^>]*>', '', desc)
    desc = desc.replace('&nbsp;', ' ')

    # 2. DATA PREP
    stats = {v['name'].strip().lower(): v['value'] for v in data_block.get("vars", [])}
    
    if not champion_name:
        champion_name = data_block.get("name") or data_block.get("mName") or ""
        
    champ_key = str(champion_name).lower().strip()

    # 3. MAPPING STRUCTURES
    # Values based on 1-Star stats
    CHAMP_BASE_STATS = {
        "ashe": {"hp": None, "ad": 58},
        "dr. mundo": {"hp": 900, "ad": None},
        "jinx": {"hp": None, "ad": 50},
        "nasus": {"hp": 1500, "ad": None},
        "nautilus": {"hp": 900, "ad": None},
        "rift herald": {"hp": 1100, "ad": None},
        "ryze": {"hp": 1000, "ad": None},
        "sion": {"hp": 650, "ad": None},
        "swain": {"hp": 1200, "ad": None},
        "volibear": {"hp": 1200, "ad": None},
        "wukong": {"hp": 1050, "ad": None},
        "yasuo": {"hp": None, "ad": 45},
        "yorick": {"hp": 850, "ad": None},

    }
    SPECIFIC_EXCEPTIONS = {
        "aatrox": {
            "firstcastmodifieddamage": (["addamage", "apdamage"], None),
            "secondcastmodifieddamage": (["addamage", "apdamage"], "secondcastpercentdamage"),
            "thirdcastmodifieddamage": (["addamage", "apdamage"], "thirdcastpercentdamage"),
        },
        "annie": { 
            "modifieddamage": (["damage"], None),
            "modifiedsecondarydamage": (["singletargetdamage"], None)
        },
        "ashe": {
            "smallarrowdamagefinal": (["smallarrowdamage*base_ad"], None)
        },
        "aphelios": {
            "modifieddamage": (["severumaddamage"], None)
        },
        "azir": {
            "modifiedsecondarydamage": (["maxsummonsdamage"], None)
        },
        "baron nashor": {
            "modifiedaciddamage": (["addamage", "apdamage"], "acidpercentdamage"),
        },
        "braum": {
            "modifieddurability": (["damagereduction"], None),
            "modifieddamage": (["apdamage", "armordamage*60"], None)
        },
        "briar": {
            "modifiedattackspeed": (["decayingattackspeed*100"], None),
        },
        "blitzcrank": {
            "modifieddamage": (["mrdamageratio*40"], None),
        },
        "darius": {
            "modifiedsecondarydamage": (["physicaldamagepersecond"], None),
        },
        "dr. mundo": {
            "totalhealing": (["percenthealthhealingpersecond*base_hp", "aphealpersecond"], None),
            "totaldamage": (["percentmaximumhealthdamage*base_hp", "addamage"], None)
        },
        "fizz": {
            "modifiedattackdamage": (["damageonhit"], None),
        },
        "galio": {
            "bonuspassivedamage": (["passivemrratio*65"], None),
            "modifiedactivedamage": (["activeardamage*65", "activemrdamage*65"], None)
        },
        "gwen": {
            "modifiedcastsniptimes": (["snipcount"], None),
            "modifieddamage": (["damage"], None),
            "modifiedsecondarydamage": (["secondarymagicdamage"], None),
        },
        "jarvan iv": {
            "modifiedattackspeed": (["attackspeed*100"], None),
        },
        "jinx": {
            "totaldamage": (["addamage","apdamage"], None) ,
        },
        "kalista": {
            "totalnumberofspears": (["basespears"], None),
        },
        "kindred": {
            "modifiedhealpercentage": (["healpercentage*100"], None),
        },
        "leona": {
            "modifieddamagereduction": (["flatdr"], None),
        },
        "lux": {
            "modifieddamage_q": (["qdamage"], None),
        },
        "mel": {
            "modifiedsecondarydamage": (["targetdamage"], None),
            "tftunitproperty.:tft16_mel_manaspent": (["0"], None),
        },
        "milio": {
            "modifiedaoedamage": (["magicdamageaoe"], None),
        },
        "miss fortune": {
            "modifiedsecondarydamage": (["addamage", "apdamage"], "percentdamageofsecondarywaves"),
        },
        "nautilus": {
            "modifieddamage": (["mrdamageratio*50"], None),
            "modifiedshield": (["apshield","percenthealthshield*base_hp"], None),
        },
        "nasus": {
            "modifieddamagepersecond": (["percenthealthdamagepersecond*base_hp"], None),
        },
        "orianna": {
            "modifiedsecondarydamage": (["targetdamage"], None),
        },
        "rek'sai": {
            "modifiedsecondarydamage": (["spellattackdamage"], None),
        },
        "renekton": {
            "modifieddashdamage": (["dashaddamage"], None),
            "modifiedslashdamage": (["slashaddamage", "slashapdamage"], None),
        },
        "rift herald": {
            "modifieddurability": (["bonusdurability*100"], None),
            "modifieddamage": (["apdamage", "percenthealthdamage*base_hp"], None),
        },
        "rumble": {
            "modifiedshield": (["apshield"], None),
            # PercentArmorDamage * Base Armor (60)
            "totaldamage": (["percentarmordamage*40"], None)
        },
        "ryze": {
            "modifiedshadowislesbonusdamage": (["shadowislesbasepercentage*100"], None),
            "modifieddemaciaexecutethreshold": (["demaciaexecutethreshold*100"], None),
            "modifiedfreljordtruedamage": (["freljordtruedamagepercenthealth*base_hp"], None),
        },
        "sett": {
            "modifiedpercentoftargetmaxhealth": (["percentoftargetmaxhealth*100"], None),
        },
        "shyvana": {
            "modifieddivebombdamage": (["divebombaddamage"], None),
            "modifiedfiredamagepersecond":(["firedamagetaddamagepersecond", "firedamageappersecond"], None)
        },
        "singed": {
            "modifiedmanapersec": (["manapercentas*0.7"], None),
        },
        "sion": {
            "modifiedshield": (["apshield", "percenthealthshield*base_hp"], None),
            "modifieddamage": (["damagepercenthealth*base_hp"], None),
        },
        "skarner": {
            "modifieddamage": (["damagepercentarmor*70"], None),
        },
        "swain": {
            "modifiedhanddamage": (["activedamage"], None),
            "totalhealing": (["aphealing", "percentmaximumhealthhealing*base_hp"], None),
        },
        "t-hex": {
            "modifiedlaserdamagepersecond": (["apdamage","addamage"], None),
            "modifiedmissiledamage": (["apdamage","addamage"], "missiledamagemult"),
        },
        "thresh": {
            "modifiedhealthdrain": (["appassivedamage"], None),
        },
        "tryndamere": {
            "modifieddurability": (["dr*100"], None),
        },
        "vi": {
            "modifiedsecondarydamage": (["secondaryaddamage"], None),
        },
        "viego": {
            "modifiedattackspeed": (["baseattackspeed"], None),
        },
        "volibear": {
            "modifiedbitedamage": (["bitedamagebase", "bitedamagehealth*base_hp"], None),
            "modifiedslamdamage": (["bitedamagebase", "bitedamagehealth*base_hp"], "slamdamagemultiplier"),
            "modifiedboltdamage": (["stormbringerboltbase", "stormbringerbolthealth*base_hp"], None),
        },
        "warwick": {
            "modifiedtakedownattackspeed": (["allyattackspeed*100"], None),
        },
        "wukong": {
            "modifieddefenses": (["resists"], None),
            "modifiedclonehealth": (["summonmaxhealthpercent*base_hp"], None),
        },
        "yasuo": {
            "yasuoadpercent*100": (["base_ad"], None),
        },
        "yorick": {
            "modifiedheal": (["apheal"], None),
            "modifieddamage": (["flatdamage","percenthealthdamage*base_hp"], None),
        },
        "zaahen": {
            "modifiedbigaoedamage": (["apdamage","addamage"], "bigaoedamagemultiplier"),
            "modifieddamage": (["apdamage","addamage"], "aoedamagemultiplier"),
        },
        "ziggs": {
            "modifiedbasicattackdamage": (["bapercentap"], None),
            "modifiedmindamage": (["minaoedamage"], None),
            "modifiedmaxdamage": (["maxaoedamage"], None),
        },
        "zilean": {
            "modifieddamage": (["magicdamage"], None),
            "modifiedsecondarydamage": (["explosiondamage"], None),
        },


    }

    GLOBAL_EXCEPTIONS = {
        "totaldamage": (["addamage", "apdamage"], None),

    }

    current_champ_map = SPECIFIC_EXCEPTIONS.get(champ_key, {})

    def format_star_values(vals):
        if not vals: return "???"
        if all(x == vals[0] for x in vals): return str(vals[0])
        if len(vals) >= 3 and vals[2] == 0 and vals[0] != 0:
            return f"{vals[0]}/{vals[1]}"
        return "/".join(map(str, [str(v).rstrip('0').rstrip('.') if '.' in str(v) else v for v in vals]))

    # 4. ICON REPLACEMENT
    icon_map = {'%i:scaleap%': 'AP', '%i:scalead%': 'AD', '%i:scaleas%': 'AS', 
                '%i:scalehealth%': 'HP', '%i:scalearmor%': 'Armor', '%i:scalemr%': 'MR'}
    
    def clean_icons(match):
        found = re.findall(r'%i:scale\w+%', match.group(0).lower())
        if not found: return ""
        labels = [icon_map.get(i, i.replace('%i:scale', '').replace('%', '')) for i in found]
        return f"({', '.join(labels)})"

    desc = re.sub(r'\((%i:scale\w+%)+\)', clean_icons, desc, flags=re.IGNORECASE)

    # 5. TOKEN REPLACEMENT
    def replace_token(match):
        raw_token = match.group(1)
        multiplier = 1.0
        
        token_name = raw_token
        if '*' in raw_token:
            token_name, factor = raw_token.split('*')
            try: multiplier = float(factor)
            except: multiplier = 1.0
        
        token_lower = token_name.lower().strip()

        # --- SETUP BASE STATS ---
        base_info = CHAMP_BASE_STATS.get(champ_key, {"hp": 0, "ad": 0})
        scaling_map = {
            1: {"hp": (base_info.get("hp") or 0), "ad": (base_info.get("ad") or 0)},
            2: {"hp": round((base_info.get("hp") or 0) * 1.8), "ad": round((base_info.get("ad") or 0) * 1.5)},
            3: {"hp": round((base_info.get("hp") or 0) * 3.24), "ad": round((base_info.get("ad") or 0) * 2.25)}
        }
        
        rule = SPECIFIC_EXCEPTIONS.get(champ_key, {}).get(token_lower) or GLOBAL_EXCEPTIONS.get(token_lower)

        if rule:
            sum_keys, mult_key = rule
            star_values = []
            for i in range(1, 4):
                base_sum = 0
                for key in sum_keys:
                    local_mult = 1.0
                    clean_key = key
                    if '*' in key:
                        clean_key, factor = key.split('*')
                        if factor == "base_hp": local_mult = scaling_map[i]["hp"]
                        elif factor == "base_ad": local_mult = scaling_map[i]["ad"]
                        else:
                            try: local_mult = float(factor)
                            except: local_mult = 1.0

                    val_raw = stats.get(clean_key.strip().lower(), [0]*7)
                    if val_raw is None: val_raw = [0]*7
                    if not isinstance(val_raw, list): val_raw = [val_raw]*7
                    val_list = [x if x is not None else 0 for x in val_raw]
                    val = val_list[i] if i < len(val_list) else val_list[0]
                    
                    DECREASING_STATS = ["mana", "attacks", "requirement", "cooldown"]
                    is_decreasing_stat = any(word in token_lower for word in DECREASING_STATS)
                    
                    if i == 3 and not is_decreasing_stat:
                        if float(val) < float(val_list[1]) and any(x > val for x in val_list):
                            val = max(val_list)
                    base_sum += float(val) * local_mult
                
                if mult_key:
                    m_list = stats.get(mult_key.lower(), [1]*7)
                    if not isinstance(m_list, list): m_list = [m_list]*7
                    m_val = m_list[i] if (i < len(m_list) and m_list[i] != 0) else m_list[0]
                    final = base_sum * float(m_val or 0) * multiplier
                else:
                    final = base_sum * multiplier
                
                is_time = any(word in token_lower for word in ["seconds", "duration"])
                is_percent = any(word in token_lower for word in ["percent", "ratio", "durability"])
                if not is_time and is_percent and 0 < final < 2: final *= 100
                star_values.append(round(final, 2) if is_time else round(final))
            return format_star_values(star_values)

        # STANDARD AGGREGATION FALLBACK
        base_name = token_lower.replace('modified', '').replace('total', '')
        relevant_vals = [val for key, val in stats.items() if base_name in key and "percent" not in key and "ratio" not in key]
        if token_lower in stats: relevant_vals = [stats[token_lower]]
        if not relevant_vals: return "???"

        star_values = []
        for i in range(1, 4):
            current_sum = 0
            for v in relevant_vals:
                try:
                    val = v[i] if isinstance(v, list) else v
                    if i == 3 and isinstance(v, list) and val < v[1]: val = max(v)
                    if val is not None: current_sum += float(val)
                except: continue
            final = current_sum * multiplier
            is_time = any(word in token_lower for word in ["seconds", "duration"])
            if not is_time and ("percent" in token_lower or "ratio" in token_lower) and 0 < final < 2: final *= 100
            star_values.append(round(final, 2) if is_time else round(final))
        return format_star_values(star_values)

    # 6. KEYWORD HANDLING
    keyword_map = {
        "{{TFT_Keyword_Sunder}}": "Sunder: Reduce Armor",
        "{{TFT_Keyword_Shred}}": "Shred: Reduce Magic Resist",
        "{{TFT_Keyword_Chill}}": "Chill: Reduce Attack Speed",
        "{{TFT_Keyword_Wound}}": "Wound: Reduce healing received by 33%",
        "{{TFT_Keyword_Burn}}": "Burn: Deal a percent of the target's max Health as true damage every second",
    }

    # Execute Token Replacement
    final_desc = re.sub(r'@([^@]+)@', replace_token, desc)

    # Process Keywords
    found_keywords = []
    for key, text in keyword_map.items():
        if key in final_desc:
            # We remove the placeholder from the main body to keep it clean
            final_desc = final_desc.replace(key, "")
            found_keywords.append(text)

    # Cleanup extra whitespace before adding keyword block
    final_desc = re.sub(r'\s+', ' ', final_desc).strip()

    # Append keyword block at the bottom
    if found_keywords:
        keyword_block = "\n" + "\n".join([f"<keyword>{kw}</keyword>" for kw in found_keywords])
        final_desc += keyword_block

    return final_desc

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