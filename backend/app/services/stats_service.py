from sqlalchemy import func, text
import re
from contextlib import contextmanager

from app.database import SessionLocal
from app.models.champion import Champion
from app.models.items import Item
from app.models.champion_item_stats import ChampionItemStats
from app.models.champion_item_valid_pairs import ChampionItemValidPairs
from app.models.champion_stats import ChampionStat
from app.services.patch_service import get_current_patch


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CURRENT_PATCH = get_current_patch()

DECREASING_STATS = ["attacks", "mana", "requirement", "cooldown"]

keyword_map = {
    "{{TFT_Keyword_Sunder}}": "Sunder: Reduce Armor",
    "{{TFT_Keyword_Shred}}": "Shred: Reduce Magic Resist",
    "{{TFT_Keyword_Chill}}": "Chill: Reduce Attack Speed",
    "{{TFT_Keyword_Wound}}": "Wound: Reduce healing received by 33%",
    "{{TFT_Keyword_Burn}}": "Burn: Deal a percent of the target's max Health as true damage every second",
}

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
        "secondcastmodifieddamage": (
            ["addamage", "apdamage"],
            "secondcastpercentdamage",
        ),
        "thirdcastmodifieddamage": (["addamage", "apdamage"], "thirdcastpercentdamage"),
    },
    "annie": {
        "modifieddamage": (["damage"], None),
        "modifiedsecondarydamage": (["singletargetdamage"], None),
    },
    "ashe": {"smallarrowdamagefinal": (["smallarrowdamage*base_ad"], None)},
    "azir": {"modifiedsecondarydamage": (["maxsummonsdamage"], None)},
    "baron nashor": {
        "modifiedaciddamage": (["addamage", "apdamage"], "acidpercentdamage"),
    },
    "bel'veth": {
        "modifiedattackspeed": (["attackspeedontransform*100"], None),
    },
    "braum": {
        "modifieddurability": (["damagereduction"], None),
        "modifieddamage": (["apdamage", "armordamage*60"], None),
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
        "totalhealing": (
            ["percenthealthhealingpersecond*base_hp", "aphealpersecond"],
            None,
        ),
        "totaldamage": (["percentmaximumhealthdamage*base_hp", "addamage"], None),
    },
    "fizz": {
        "modifiedattackdamage": (["damageonhit"], None),
    },
    "galio": {
        "bonuspassivedamage": (["passivemrratio*65"], None),
        "modifiedactivedamage": (["activeardamage*65", "activemrdamage*65"], None),
    },
    "gwen": {
        "modifiedcastsniptimes": (["snipcount"], None),
        "modifieddamage": (["damage"], None),
        "modifiedsecondarydamage": (["secondarymagicdamage"], None),
    },
    "jarvan iv": {
        "modifiedattackspeed": (["attackspeed*100"], None),
    },
    "kalista": {
        "totalnumberofspears": (["basespears"], None),
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
        "modifiedsecondarydamage": (
            ["addamage", "apdamage"],
            "percentdamageofsecondarywaves",
        ),
    },
    "nautilus": {
        "modifieddamage": (["mrdamageratio*50"], None),
        "modifiedshield": (["apshield", "percenthealthshield*base_hp"], None),
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
        "totaldamage": (["percentarmordamage*40"], None),
    },
    "ryze": {
        "modifiedshadowislesbonusdamage": (["shadowislesbasepercentage*100"], None),
        "modifieddemaciaexecutethreshold": (["demaciaexecutethreshold*100"], None),
        "modifiedfreljordtruedamage": (
            ["freljordtruedamagepercenthealth*base_hp"],
            None,
        ),
    },
    "sett": {
        "modifiedpercentoftargetmaxhealth": (["percentoftargetmaxhealth*100"], None),
    },
    "shyvana": {
        "modifieddivebombdamage": (["divebombaddamage"], None),
        "modifiedfiredamagepersecond": (
            ["firedamagetaddamagepersecond", "firedamageappersecond"],
            None,
        ),
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
        "modifiedlaserdamagepersecond": (["apdamage", "addamage"], None),
        "modifiedmissiledamage": (["apdamage", "addamage"], "missiledamagemult"),
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
        "modifiedslamdamage": (
            ["bitedamagebase", "bitedamagehealth*base_hp"],
            "slamdamagemultiplier",
        ),
        "modifiedboltdamage": (
            ["stormbringerboltbase", "stormbringerbolthealth*base_hp"],
            None,
        ),
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
    "yone": {
        "modifiedpertargetdamage": (["pertargetaddamage", "pertargetapdamage"], None),
        "modifiedstrikedamage": (["strikeaddamage", "strikeapdamage"], None),
    },
    "yunara": {
        "modifiedattackspeed": (["attackspeed*100"], None),
    },
    "yorick": {
        "modifiedheal": (["apheal"], None),
        "modifieddamage": (["flatdamage", "percenthealthdamage*base_hp"], None),
    },
    "zaahen": {
        "modifiedbigaoedamage": (["apdamage", "addamage"], "bigaoedamagemultiplier"),
        "modifieddamage": (["apdamage", "addamage"], "aoedamagemultiplier"),
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


def get_sorted_traits(traits):
    """
    Filters out 'duo' traits, then sorts: Unique > Origin > Class.
    Alphabetical within the same type.
    """
    filtered_traits = [t for t in traits if t.type != "duo"]

    priority = {"unique": 0, "origin": 1, "class": 2}

    sorted_list = sorted(
        filtered_traits, key=lambda t: (priority.get(t.type, 99), t.name)
    )

    return [{"name": t.name, "type": t.type, "riot_id": t.riot_id} for t in sorted_list]


def get_champion_special_items(champion_riot_id: str):
    with get_db() as db:
        champion = (
            db.query(Champion).filter(Champion.riot_id == champion_riot_id).first()
        )

        if not champion:
            return None

        sorted_traits = get_sorted_traits(champion.traits)

        readable_ability = render_champion_description(
            champion.ability_desc, champion.ability_variables, champion.name
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

        total_games = sum(row.count for row in stats)

        item_ids = [row.item_id for row in stats]

        item_map = {i.id: i for i in db.query(Item).filter(Item.id.in_(item_ids)).all()}

        valid_item_ids = {
            row.item_id
            for row in db.query(ChampionItemValidPairs.item_id)
            .filter(ChampionItemValidPairs.champion_id == champion.id)
            .all()
        }

        overall_avgs_by_item_id = {
            row.item_id: float(row.avg_placement)
            for row in db.query(
                ChampionItemStats.item_id,
                func.avg(ChampionItemStats.placement).label("avg_placement"),
            )
            .filter(ChampionItemStats.normalized_patch == CURRENT_PATCH)
            .group_by(ChampionItemStats.item_id)
            .all()
        }

        artifacts = {}
        radiants = {}

        for item_id, count, avg in stats:
            item = item_map.get(item_id)
            if not item:
                continue

            percentage = count / total_games if total_games else 0
            avg_placement = float(avg)
            overall_avg = overall_avgs_by_item_id.get(item_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            data = {
                "name": item.name,
                "count": count,
                "average_placement": avg_placement,
                "delta": delta,
                "type": item.type,
                "valid": item_id in valid_item_ids,
                "low_sample": percentage < 0.01,
            }

            if item.type == "artifact":
                artifacts[item.riot_id] = data
            elif item.type == "radiant":
                radiants[item.riot_id] = data

    artifacts = dict(sorted(artifacts.items(), key=lambda x: (x[1]["average_placement"] is None, x[1]["average_placement"])))
    radiants = dict(sorted(radiants.items(), key=lambda x: (x[1]["average_placement"] is None, x[1]["average_placement"])))

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


def get_item_stats_by_id(item_riot_id: str, item_type: str):
    with get_db() as db:
        item = (
            db.query(Item)
            .filter(Item.riot_id == item_riot_id, Item.type == item_type)
            .first()
        )

        if not item:
            return None

        readable_desc = render_item_data(item.description, item.effects)

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

        total_games = sum(row.count for row in stats)

        champion_ids = [row.champion_id for row in stats]

        champion_map = {
            c.id: c
            for c in db.query(Champion).filter(Champion.id.in_(champion_ids)).all()
        }

        valid_champion_ids = {
            row.champion_id
            for row in db.query(ChampionItemValidPairs.champion_id)
            .filter(ChampionItemValidPairs.item_id == item.id)
            .all()
        }

        overall_avgs_by_riot_id = {
            row.champion_id: float(row.avg_placement)
            for row in db.query(
                ChampionStat.champion_id,
                func.avg(ChampionStat.placement).label("avg_placement"),
            )
            .join(Champion, Champion.riot_id == ChampionStat.champion_id)
            .group_by(ChampionStat.champion_id)
            .all()
        }

        result = {}

        for champion_id, count, avg in stats:
            champion = champion_map.get(champion_id)
            if not champion:
                continue

            percentage = count / total_games if total_games else 0
            avg_placement = float(avg)
            overall_avg = overall_avgs_by_riot_id.get(champion.riot_id)
            delta = round(avg_placement - overall_avg, 2) if overall_avg is not None else None

            result[champion.riot_id] = {
                "name": champion.name,
                "count": count,
                "average_placement": avg_placement,
                "delta": delta,
                "valid": champion_id in valid_champion_ids,
                "low_sample": percentage < 0.01,
            }

    sorted_result = dict(
    sorted(result.items(), key=lambda x: (x[1]["delta"] is None, x[1]["delta"]))
    )

    return {
        "id": item_riot_id,
        "name": item.name,
        "type": item_type,
        "description": readable_desc,
        "stats": item.effects,
        "champions": sorted_result,
    }


def _resolve_token_fuzzy(token_lower: str, stats: dict) -> dict | None:
    """
    Attempts to automatically resolve Modified*/Total*/Bonus* tokens
    by stripping the prefix and finding matching vars in stats.
    Returns a dict of {var_name: value} or None if nothing found.
    """
    base = token_lower
    for prefix in ("modified", "total", "bonus"):
        if base.startswith(prefix):
            base = base[len(prefix) :]
            break

    if not base:
        return None

    matches = {k: v for k, v in stats.items() if base in k}

    if not matches:
        return None

    non_percent = {
        k: v for k, v in matches.items() if "percent" not in k and "ratio" not in k
    }

    return non_percent if non_percent else matches


def render_champion_description(desc, data_block, champion_name):
    if not desc:
        return ""

    desc = re.sub(
        r"<spellPassive>\s*Passive\s*:\s*</spellPassive>\s*",
        "\nPassive: ",
        desc,
        flags=re.IGNORECASE,
    )
    desc = re.sub(
        r"<spellActive>\s*Active\s*:\s*</spellActive>\s*",
        "\nActive: ",
        desc,
        flags=re.IGNORECASE,
    )
    desc = re.sub(r"<spellPassive>|</spellPassive>", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"<spellActive>|</spellActive>", "", desc, flags=re.IGNORECASE)
    desc = re.sub(r"<br\s*/?>", "\n", desc, flags=re.IGNORECASE)
    desc = re.sub(r"<[^>]*>", "", desc)
    desc = desc.replace("&nbsp;", " ")
    desc = re.sub(r"%i:(?!scale)[^%]+%", "", desc)

    stats = {v["name"].strip().lower(): v["value"] for v in data_block.get("vars", [])}

    if not champion_name:
        champion_name = data_block.get("name") or data_block.get("mName") or ""

    champ_key = str(champion_name).lower().strip()

    PERCENT_TOKENS = [
        "attackspeed",
        "durability",
        "omnivamp",
        "crit",
        "modifiedattackspeed",
        "modifiedhealpercentage",
        "modifiedpercentoftargetmaxhealth",
        "modifieddurability",
        "modifieddamagereduction",
    ]

    def needs_percent_suffix(token_lower):
        return any(kw in token_lower for kw in PERCENT_TOKENS)

    def format_star_values(vals, suffix=""):
        if not vals:
            return "???"
        str_vals = [str(v) for v in vals]
        if all(v == str_vals[0] for v in str_vals):
            return f"{str_vals[0]}{suffix}"
        if (
            len(vals) >= 3
            and str(vals[2]) in ("0", "0%")
            and str(vals[0]) not in ("0", "0%")
        ):
            return f"{vals[0]}{suffix}/{vals[1]}{suffix}"
        return "/".join(f"{v}{suffix}" for v in str_vals)

    icon_map = {
        "%i:scaleap%": "AP",
        "%i:scalead%": "AD",
        "%i:scaleas%": "AS",
        "%i:scalehealth%": "HP",
        "%i:scalearmor%": "Armor",
        "%i:scalemr%": "MR",
    }

    def clean_icons(match):
        found = re.findall(r"%i:scale\w+%", match.group(0).lower())
        if not found:
            return ""
        labels = [
            icon_map.get(i, i.replace("%i:scale", "").replace("%", "")) for i in found
        ]
        return f"({', '.join(labels)})"

    desc = re.sub(r"\((%i:scale\w+%)+\)", clean_icons, desc, flags=re.IGNORECASE)

    def replace_token(match):
        raw_token = match.group(1)
        multiplier = 1.0

        token_name = raw_token
        if "*" in raw_token:
            token_name, factor = raw_token.split("*")
            try:
                multiplier = float(factor)
            except:
                multiplier = 1.0

        token_lower = token_name.lower().strip()

        base_info = CHAMP_BASE_STATS.get(champ_key, {"hp": 0, "ad": 0})
        scaling_map = {
            1: {"hp": (base_info.get("hp") or 0), "ad": (base_info.get("ad") or 0)},
            2: {
                "hp": round((base_info.get("hp") or 0) * 1.8),
                "ad": round((base_info.get("ad") or 0) * 1.5),
            },
            3: {
                "hp": round((base_info.get("hp") or 0) * 3.24),
                "ad": round((base_info.get("ad") or 0) * 2.25),
            },
        }

        def append_percent(value):
            if "*" in raw_token and needs_percent_suffix(token_lower):
                return f"{value}%"
            return f"{value}%" if needs_percent_suffix(token_lower) else value

        rule = SPECIFIC_EXCEPTIONS.get(champ_key, {}).get(
            token_lower
        ) or GLOBAL_EXCEPTIONS.get(token_lower)

        if rule:
            sum_keys, mult_key = rule
            star_values = []
            suffix = "%" if needs_percent_suffix(token_lower) else ""
            for i in range(1, 4):
                base_sum = 0
                for key in sum_keys:
                    local_mult = 1.0
                    clean_key = key
                    if "*" in key:
                        clean_key, factor = key.split("*")
                        if factor == "base_hp":
                            local_mult = scaling_map[i]["hp"]
                        elif factor == "base_ad":
                            local_mult = scaling_map[i]["ad"]
                        else:
                            try:
                                local_mult = float(factor)
                            except:
                                local_mult = 1.0

                    val_raw = stats.get(clean_key.strip().lower(), [0] * 7)
                    if val_raw is None:
                        val_raw = [0] * 7
                    if not isinstance(val_raw, list):
                        val_raw = [val_raw] * 7
                    val_list = [x if x is not None else 0 for x in val_raw]
                    val = val_list[i] if i < len(val_list) else val_list[0]

                    is_decreasing_stat = any(
                        word in token_lower for word in DECREASING_STATS
                    )
                    is_time = any(
                        word in token_lower for word in ["seconds", "duration"]
                    )

                    if i == 3 and not is_decreasing_stat and not is_time:
                        if float(val) < float(val_list[1]) and any(
                            x > val for x in val_list
                        ):
                            val = max(val_list)
                    base_sum += float(val) * local_mult

                if mult_key:
                    m_list = stats.get(mult_key.lower(), [1] * 7)
                    if not isinstance(m_list, list):
                        m_list = [m_list] * 7
                    m_val = (
                        m_list[i] if (i < len(m_list) and m_list[i] != 0) else m_list[0]
                    )
                    final = base_sum * float(m_val or 0) * multiplier
                else:
                    final = base_sum * multiplier

                is_time = any(word in token_lower for word in ["seconds", "duration"])
                is_percent = any(
                    word in token_lower for word in ["percent", "ratio", "durability"]
                )
                if not is_time and is_percent and 0 < final < 2:
                    final *= 100
                formatted = round(final, 2) if is_time else round(final)
                star_values.append(formatted)
            return format_star_values(star_values, suffix)

        fuzzy_matches = _resolve_token_fuzzy(token_lower, stats)
        if fuzzy_matches:
            star_values = []
            suffix = "%" if needs_percent_suffix(token_lower) else ""
            for i in range(1, 4):
                current_sum = 0
                for v in fuzzy_matches.values():
                    try:
                        val_list = v if isinstance(v, list) else [v] * 7
                        val_list = [x if x is not None else 0 for x in val_list]
                        val = val_list[i] if i < len(val_list) else val_list[0]

                        is_decreasing_stat = any(
                            w in token_lower for w in DECREASING_STATS
                        )
                        is_time = any(
                            word in token_lower for word in ["seconds", "duration"]
                        )

                        if i == 3 and not is_decreasing_stat and not is_time:
                            if float(val) < float(val_list[1]) and any(
                                x > val for x in val_list
                            ):
                                val = max(val_list)

                        current_sum += float(val) * multiplier
                    except:
                        continue

                is_time = any(w in token_lower for w in ["seconds", "duration"])
                is_percent = any(
                    w in token_lower for w in ["percent", "ratio", "durability"]
                )
                if not is_time and is_percent and 0 < current_sum < 2:
                    current_sum *= 100
                formatted = round(current_sum, 2) if is_time else round(current_sum)
                star_values.append(formatted)
            return format_star_values(star_values, suffix)

        base_name = token_lower.replace("modified", "").replace("total", "")
        relevant_vals = [
            val
            for key, val in stats.items()
            if base_name in key and "percent" not in key and "ratio" not in key
        ]
        if token_lower in stats:
            relevant_vals = [stats[token_lower]]
        if not relevant_vals:
            return "???"

        star_values = []
        suffix = "%" if needs_percent_suffix(token_lower) else ""
        for i in range(1, 4):
            current_sum = 0
            for v in relevant_vals:
                try:
                    val = v[i] if isinstance(v, list) else v
                    if i == 3 and isinstance(v, list) and val < v[1]:
                        val = max(v)
                    if val is not None:
                        current_sum += float(val)
                except:
                    continue
            final = current_sum * multiplier
            is_time = any(word in token_lower for word in ["seconds", "duration"])
            if (
                not is_time
                and ("percent" in token_lower or "ratio" in token_lower)
                and 0 < final < 2
            ):
                final *= 100
            formatted = round(final, 2) if is_time else round(final)
            star_values.append(formatted)
        return format_star_values(star_values, suffix)


    final_desc = re.sub(r"@([^@]+)@", replace_token, desc)
    final_desc = final_desc.replace("%%", "%")

    found_keywords = []
    for key, text in keyword_map.items():
        if key in final_desc:
            final_desc = final_desc.replace(key, "")
            found_keywords.append(text)

    final_desc = re.sub(r"[^\S\n]+", " ", final_desc).strip()

    if found_keywords:
        keyword_block = "\n" + "\n".join(
            [f"<keyword>{kw}</keyword>" for kw in found_keywords]
        )
        final_desc += keyword_block

    return final_desc


def render_item_data(desc, effects_raw):
    if not desc:
        return "", effects_raw

    desc = re.sub(r"<br\s*/?>", "\n", desc, flags=re.IGNORECASE)

    desc = re.sub(
        r"<TFTShadowItemBonus>(.*?)</TFTShadowItemBonus>",
        r"\1",
        desc,
        flags=re.IGNORECASE | re.DOTALL,
    )
    desc = re.sub(
        r"<TFTRadiantItemBonus>(.*?)</TFTRadiantItemBonus>",
        r"\1",
        desc,
        flags=re.IGNORECASE | re.DOTALL,
    )
    desc = re.sub(
        r"<TFTKeyword>(.*?)</TFTKeyword>", r"\1", desc, flags=re.IGNORECASE | re.DOTALL
    )
    desc = re.sub(
        r"<tftbold>(.*?)</tftbold>", r"\1", desc, flags=re.IGNORECASE | re.DOTALL
    )

    desc = re.sub(
        r"<TFTTrackerLabel>.*?</TFTTrackerLabel>\s*<TFTHighlight>.*?</TFTHighlight>",
        "",
        desc,
        flags=re.IGNORECASE | re.DOTALL,
    )

    flavor_texts_raw = re.findall(
        r"<tftitemrules>(.*?)</tftitemrules>", desc, flags=re.IGNORECASE | re.DOTALL
    )
    flavor_texts_raw += re.findall(
        r"<rules>(.*?)</rules>", desc, flags=re.IGNORECASE | re.DOTALL
    )
    flavor_texts_raw = [t.strip() for t in flavor_texts_raw if t.strip()]

    desc = re.sub(
        r"<tftitemrules>.*?</tftitemrules>", "", desc, flags=re.IGNORECASE | re.DOTALL
    )
    desc = re.sub(r"<rules>.*?</rules>", "", desc, flags=re.IGNORECASE | re.DOTALL)

    desc = re.sub(
        r"<keyword>(.*?)</keyword>",
        r"KEYWORD_START\1KEYWORD_END",
        desc,
        flags=re.IGNORECASE | re.DOTALL,
    )

    desc = re.sub(r"<[^>]*>", "", desc)
    desc = desc.replace("&nbsp;", " ")
    desc = desc.replace("KEYWORD_START", "<keyword>").replace(
        "KEYWORD_END", "</keyword>"
    )

    desc = re.sub(r"%i:[^%]+%", "", desc)

    def replace_token(token_str):
        if "TFTUnitProperty" in token_str:
            return "X"

        multiplier = 1.0
        if "*" in token_str:
            token_str, factor = token_str.split("*")
            try:
                multiplier = float(factor)
            except:
                multiplier = 1.0

        val = effects_raw.get(token_str)
        if val is None:
            return "???"

        num = float(val)
        result = num * multiplier
        return str(round(result, 2)).rstrip("0").rstrip(".")

    def replace_token_match(match):
        return replace_token(match.group(1))

    rendered_desc = re.sub(r"@([^@]+)@", replace_token_match, desc)

    STRIP_FROM_KEYWORDS = ["[Direct damage item]"]
    found_keywords = []

    for key, text in keyword_map.items():
        if key in rendered_desc:
            rendered_desc = rendered_desc.replace(key, "")
            found_keywords.append(re.sub(r"<[^>]*>", "", text).strip())

    for raw_text in flavor_texts_raw:
        resolved = re.sub(r"@([^@]+)@", replace_token_match, raw_text)
        resolved = re.sub(
            r"<tftbold>(.*?)</tftbold>",
            r"\1",
            resolved,
            flags=re.IGNORECASE | re.DOTALL,
        )
        resolved = re.sub(r"<br\s*/?>", "\n", resolved, flags=re.IGNORECASE)
        resolved = re.sub(r"<[^>]*>", "", resolved)
        resolved = re.sub(r"%i:[^%]+%", "", resolved)
        resolved = resolved.strip()

        if not resolved:
            continue

        lines = [line.strip() for line in resolved.split("\n") if line.strip()]

        for line in lines:
            if line in STRIP_FROM_KEYWORDS:
                continue

            line = line.replace("Dash Cooldown:", "DASH_COOLDOWN_PLACEHOLDER")
            sub_parts = re.split(r"(?=[A-Z][a-z]+:)", line)
            for part in sub_parts:
                part = part.replace(
                    "DASH_COOLDOWN_PLACEHOLDER", "Dash Cooldown:"
                ).strip()
                if part:
                    found_keywords.append(part)

    rendered_desc = re.sub(r"[^\S\n]+", " ", rendered_desc)
    rendered_desc = re.sub(r"\n{3,}", "\n\n", rendered_desc).strip()

    if found_keywords:
        unique_keywords = []
        for kw in found_keywords:
            if kw not in unique_keywords:
                unique_keywords.append(kw)

        keyword_block = "\n" + "\n".join(
            [f"<keyword>{kw}</keyword>" for kw in unique_keywords]
        )
        rendered_desc = rendered_desc.rstrip() + keyword_block

    cleaned_effects = {}
    for key, val in effects_raw.items():
        if isinstance(val, (int, float)):
            if 0 < val < 1:
                cleaned_effects[key] = round(val * 100)
            else:
                cleaned_effects[key] = round(val)

    return rendered_desc
