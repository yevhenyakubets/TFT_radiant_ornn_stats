import re
from app.constants.description_constants import (
    CHAMP_BASE_STATS, SPECIFIC_EXCEPTIONS, 
    GLOBAL_EXCEPTIONS, DECREASING_STATS, keyword_map
)

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


def render_item_description(desc, effects_raw):
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
