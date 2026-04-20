import re
from app.constants.description_constants import (
    CHAMPION_EXCEPTIONS,
    GLOBAL_EXCEPTIONS,
    CHAMP_BASE_STATS,
    KEYWORD_MAP,
    ARTIFACT_HASH_MAP
)
from app.utils.helper import (
    clean_num, finalize_desc, normalize_item_variables
)

def render_champion_description(desc, data_block, champion_id):
    """
    Main entry point for champion abilities.
    Inputs:
        desc: Raw description string from Riot data.
        data_block: Dictionary containing variable values (1-3 star tiers).
        champion_id: String ID used for exception lookups.
    Returns:
        Formatted string with values injected and icons normalized.
    """
    if not desc:
        return ""
    return new_render_logic(desc, data_block, champion_id)

def render_item_description(desc, effects_raw):
    """
    Main entry point for items.
    Converts flat item effects into 3-tier lists to reuse the core rendering logic.
    Inputs:
        desc: Raw description string from Riot data.
        effects_raw: Dictionary of item stats (e.g., {'Damage': 30}).
    Returns:
        Formatted string where @Variables@ are replaced and item rules are extracted.
    """
    if not desc:
        return ""
    variables_dict = normalize_item_variables(effects_raw)

    return new_render_logic(desc, variables_dict, champion_id=None)

def new_render_logic(ability_description, variables_dict, champion_id=None):
    """
    Core rendering engine that handles variable injection, scaling icons, 
    and Riot's unique tag formatting.
    """
    if not ability_description: 
        return ""
    
    # Ensure tier lists are exactly 3 values (1/2/3 star) for the replacer logic.
    for key in list(variables_dict.keys()):
        if isinstance(variables_dict[key], list) and len(variables_dict[key]) > 3:
            variables_dict[key] = variables_dict[key][1:4]

    def replacer(match):
        """ Internal function to process @Variable@ tokens. """
        token_raw = match.group(1).strip()

        if "TFTUnitProperty" in token_raw:
            # Keep '0' for trackers (Collector), hide for scaling stats (Wit's End).
            if "Tracker" in token_raw:
                return "0"
            return ""
        
        # Handle multipliers (e.g., @Variable*100@).
        parts = token_raw.split('*')
        token_name = parts[0].replace(".:", "").strip()

        # Check for Artifact mappings (Riot occasionally uses internal hashes).
        lookup_key = ARTIFACT_HASH_MAP.get(token_name, token_name)

        val = None
        # Pull value from Exceptions (for specialized math) or directly from variables_dict.
        if champion_id and champion_id in CHAMPION_EXCEPTIONS and lookup_key in CHAMPION_EXCEPTIONS[champion_id]:
            val = CHAMPION_EXCEPTIONS[champion_id][lookup_key](variables_dict, CHAMP_BASE_STATS)
        elif lookup_key in GLOBAL_EXCEPTIONS:
            val = GLOBAL_EXCEPTIONS[lookup_key](variables_dict, CHAMP_BASE_STATS)
        else:
            val = variables_dict.get(lookup_key)
            # Support for "Modified" prefix variants.
            if val is None and lookup_key.startswith("Modified"):
                val = variables_dict.get(lookup_key.replace("Modified", "", 1))
        
        if val is None: 
            return "???"

        # Apply multiplier if present.
        multiplier = 1.0
        if len(parts) > 1:
            try: 
                multiplier = float(parts[1])
            except ValueError: 
                pass
        
        if multiplier != 1.0 and val != "???":
            if isinstance(val, list): 
                val = [v * multiplier for v in val]
            else: 
                val = val * multiplier

        # Format output: Return "X / Y / Z" or single value if all tiers match.
        if isinstance(val, list):
            formatted = [clean_num(v) for v in val]
            if len(formatted) >= 3 and (formatted[0] == formatted[1] == formatted[2]):
                return formatted[0]
            return " / ".join(formatted)
        
        return clean_num(val)

    found_keywords = []
    
    # Extract known keywords from KEYWORD_MAP.
    for key, text in KEYWORD_MAP.items():
        if key in ability_description:
            ability_description = ability_description.replace(key, "")
            found_keywords.append(text)

    # Splits multi-rule tags (Radiant items) into individual list items for the frontend.
    rules_matches = re.findall(r"<(rules|tftitemrules)>(.*?)</\1>", ability_description, flags=re.IGNORECASE | re.DOTALL)
    for match in rules_matches:
        rule_content = match[1]
        split_rules = re.split(r'<\s*br\s*/?>|[\n\r]', rule_content)

        for part in split_rules:
            processed_rule = re.sub(r"@([^@]+)@", replacer, part, flags=re.DOTALL)
            clean_rule = processed_rule.strip()
            if clean_rule and clean_rule not in found_keywords:
                found_keywords.append(clean_rule)

    final_description = re.sub(r"@([^@]+)@", replacer, ability_description, flags=re.DOTALL)
    cleaned_body = finalize_desc(final_description, champion_id)

    cleaned_keywords = [finalize_desc(kw, champion_id) for kw in found_keywords if kw]
    
    keyword_output = "".join([f"\n<keyword>{kw}</keyword>" for kw in cleaned_keywords if kw])
    
    return cleaned_body + keyword_output