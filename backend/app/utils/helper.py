import re

def get_scaling_stat(champ_id, stat_name, base_stats_map):
    """
    Calculates 1/2/3 star scaling for base stats (HP and AD).
    Inputs:
        champ_id: Internal ID for the champion.
        stat_name: The stat type (e.g., 'hp' or 'ad').
        base_stats_map: The reference dictionary for champion base values.
    Returns:
        List containing [star1, star2, star3] scaled values.
    """
    base = base_stats_map.get(champ_id, {}).get(stat_name)
    if base is None:
        return [0, 0, 0]
    
    # HP scales by 1.8x per star level; AD scales by 1.5x.
    if stat_name == "hp":
        star2 = round(base * 1.8)
        star3 = round(star2 * 1.8)
    elif stat_name == "ad":
        star2 = round(base * 1.5)
        star3 = round(star2 * 1.5)
    else:
        star2 = base
        star3 = base
        
    return [base, star2, star3]

def scale_by_base_stat(stats, champ_id, stat_type, modifier_key, base_stats_map, add_key=None, constant_modifier=None):
    """
    Scales a modifier by a champion's base stat and adds optional flat bonuses.
    Inputs:
        stats: Dictionary of current ability variables.
        stat_type: The base stat to scale with (HP/AD/Armor).
        modifier_key: The variable key for the percentage modifier.
        add_key: Optional flat value to add to the result.
    Returns:
        List of 3 rounded values.
    """
    base_vals = get_scaling_stat(champ_id, stat_type, base_stats_map)
    
    if constant_modifier is not None:
        modifiers = [constant_modifier] * 3
    else:
        modifiers = stats.get(modifier_key, [0, 0, 0])
        
    add_vals = stats.get(add_key, [0, 0, 0]) if add_key else [0, 0, 0]
    
    return [round(add_vals[i] + (base_vals[i] * modifiers[i])) for i in range(3)]

def finalize_desc(text, champ_id=None):
    """
    Final polishing station for all description strings.
    Handles strict token replacements, icon normalization, and rule removal.
    """
    if not text:
        return ""

    # literal replacements
    text = text.replace("%i:TFTBaseAD%", "AD")
    text = text.replace("&nbsp;", " ")
    text = text.replace("%i:set14AmpIcon%", "Amp") 
    text = re.sub(r"<(rules|tftitemrules)>.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)

    # normalization for scaling icons
    def format_scales(match):
        stats = re.findall(r'scale([a-zA-Z]+)', match.group(1))
        return f"({', '.join(stats)})" if stats else ""
    
    text = re.sub(r'\((%i:scale[a-zA-Z]+%.*?)\)', format_scales, text)
    text = re.sub(r'%i:scale([a-zA-Z]+)%', r'\1', text)

    # Set 17 exclusive - space groove handling
    def process_groove(match):
        name = match.group(1)
        formatted_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        return f"<groove>{formatted_name}</groove>"

    text = re.sub(r'\{\{TFT17_SpaceGroove_([a-zA-Z]+)\}\}', process_groove, text)

    # cleanup
    text = re.sub(
        r'\[\s*Direct\s*damage\s*item\s*\](<\s*br\s*/?>|[\n\r\s])*', 
        '', text, flags=re.IGNORECASE | re.DOTALL
    )
    text = re.sub(r'\(\s*[a-zA-Z]*:\s*\)', '', text)

    # Set 17 exclusive - Riven fix
    if champ_id == "Riven":
        text = text.replace("</magicDamage> magic", "</magicDamage> magic / ")

    return text.strip()

def clean_num(n):
    """
    Normalizes numbers for display, removing unnecessary decimals.
    Example: 15.0 -> "15", 15.5 -> "15.5".
    """
    try:
        if isinstance(n, (int, float)):
            n = round(n, 2)
            return str(int(n)) if n == int(n) else str(n)
        return str(n)
    except (ValueError, TypeError):
        return str(n)
    
def sum_stats(stats, keys):
    """
    Sums multiple variable keys into a single 3-tier list.
    Useful for 'ModifiedDamage' tokens that combine AD and AP.
    """
    result = [0, 0, 0]
    for k in keys:
        val = stats.get(k, 0)
        if isinstance(val, list):
            for i in range(min(len(result), len(val))):
                result[i] += val[i]
        else:
            for i in range(3): 
                result[i] += val
    return result

def sum_and_scale(stats, keys_to_sum, modifier_key):
    """
    Sums multiple stats and then multiplies the total by a scaling modifier.
    """
    base_sum = sum_stats(stats, keys_to_sum)
    modifiers = stats.get(modifier_key, [1, 1, 1])
    return [round(base_sum[i] * modifiers[i]) for i in range(3)]

def scale_and_multiply(vars_dict, champ_id, base_stat, scale_key, multiplier_key, add_key=None, base_stats_map=None):
    """
    Advanced scaling for abilities that utilize a base stat calculation 
    further modified by a separate coefficient (e.g., Nova modifiers).
    """
    # 1. Resolve the initial scaling.
    base_vals = scale_by_base_stat(
        vars_dict, champ_id, base_stat, scale_key, 
        add_key=add_key, base_stats_map=base_stats_map
    )
    
    # 2. Extract and cast multiplier.
    raw_multiplier = vars_dict.get(multiplier_key, 1.0)
    if isinstance(raw_multiplier, list):
        multiplier = float(raw_multiplier[0]) if raw_multiplier else 1.0
    else:
        multiplier = float(raw_multiplier)
    
    # 3. Apply multiplier to each tier.
    target = base_vals[0] if base_vals and isinstance(base_vals[0], list) else base_vals
    return [round(float(v) * multiplier) for v in (target or [0, 0, 0])][:3]

def normalize_item_variables(effects_raw):
    """
    Sanitization layer for item data.
    Converts flat effect values into 3-tier lists to ensure compatibility 
    with the core rendering engine.
    """
    if not effects_raw:
        return {}

    normalized = {}
    for key, val in effects_raw.items():
        if isinstance(val, list):
            if len(val) >= 3:
                normalized[key] = val[:3]
            else:
                normalized[key] = (val * 3)[:3]
        else:
            normalized[key] = [val, val, val]
            
    return normalized