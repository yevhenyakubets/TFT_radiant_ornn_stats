#Constans that are needed for description rendering
from app.utils.helper import (
    sum_stats, scale_by_base_stat, sum_and_scale, clean_num, scale_and_multiply

)

KEYWORD_MAP = {
    "{{TFT_Keyword_Sunder}}": "Sunder: Reduce Armor",
    "{{TFT_Keyword_Shred}}": "Shred: Reduce Magic Resist",
    "{{TFT_Keyword_Chill}}": "Chill: Reduce Attack Speed",
    "{{TFT_Keyword_Wound}}": "Wound: Reduce healing received by 33%",
    "{{TFT_Keyword_Burn}}": "Burn: Deal a percent of the target's max Health as true damage every second",
    "{{TFT_Keyword_Precision}}": "Precision: Ability damage can critically strike. Additional Precision grants 10% Critical Strike Damage.",
    
}

#New set 17 artifacts have hashes for their some of their stats/effects
ARTIFACT_HASH_MAP = {
    "FlatMagicDamage": "{430aee8c}",
    "PercentSpeedIncrease": "{0efd1965}",
    "AbilityDA": "{54531c4a}",
    "DecayingAS": "{1e28e4ef}",
    "ExecuteThresholdForTarget": "{72fa3d6f}",
    "NumMiracles": "{820af257}",
    "HPThreshold": "{cd951938}",
    "TotalHealRatio": "{b888d296}",
    "StackingStats": "{1b6f9b58}" 
}

#Base stats for champion that have values that scale with them. These need to be changed manually every set
CHAMP_BASE_STATS = {
    "TFT17_Aatrox": {"hp": 700, "armor": 45},
    "TFT17_Gnar": {"ad": 45},
    "TFT17_Rammus": {"armor": 60},
    "TFT17_Maokai": {"hp": 1100},
    "TFT17_Galio": {"armor": 60, "mr": 60},
    "TFT17_Gragas": {"hp": 850},
    "TFT17_Nasus": {"hp": 700, },
    "TFT17_Jax": {"armor": 50, "mr": 50},
    "TFT17_Shen": {"hp": 1200},
    "TFT17_Chogath": {"hp": 1000},
    "TFT17_Graves": {"ad": 60},
    "TFT17_TahmKench": {"hp": 1300},
    "TFT17_Reksai": {"hp": 700},
    "TFT17_Pantheon": {"hp": 900},
}

#An extensive map for token matching for champion descriptions
#Tokens provided in raw Riot data aren't consistent, so the ones that don't follow a pattern need to be mapped manually, changes every set
CHAMPION_EXCEPTIONS = {
    "Aatrox": {
        "ModifiedHeal": lambda s, m: scale_by_base_stat(
            s, "TFT17_Aatrox", "hp", "HealHP", base_stats_map=m, add_key="HealAP"
        ),
        "ModifiedDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Aatrox", "armor", "DamagePercentArmor", base_stats_map=m, add_key="DamageAD"
        ),
        "ModifiedNovaDamage": lambda s, m: scale_and_multiply(
            vars_dict=s,
            champ_id="TFT17_Aatrox",
            base_stat="armor",
            scale_key="DamagePercentArmor",
            multiplier_key="NOVAModifier",
            add_key="DamageAD",
            base_stats_map=m
        )
    },
    "Bel'Veth": { 
        "TotalNumSlashes": lambda s, m: s.get("BaseNumSlashes", 0), 
    },
    "Briar": { 
        "ModifiedDamage": lambda s, m: sum_stats(s, ["ADDamage", "APDamage"]),
    },
    "Akali": { 
        "ModifiedDamage": lambda s, m: sum_stats(s, ["DamageAD", "DamageAP"]),
        "ModifiedSecondaryDamage": lambda s, m: sum_and_scale(s, ["DamageAP", "DamageAD"], "SecondaryDamageModifier"),
        "ModifiedNovaDamage": lambda s, m: s.get("NovaDamagePerSecond", 0), 
    },
    "Bard": { 
        "ModifiedNumAllies": lambda s, m: s.get("MeepsPerMeep", 0),      
    },
    "Jinx": { 
        "ModifiedNumRockets": lambda s, m: s.get("BaseBullets", 0),    
    },
    "Gnar": { 
        "ModifiedDamage": lambda s, m: sum_stats(s, ["DamageAD", "DamageAP"]),
        "ModifiedMeepDPS": lambda s, m: scale_by_base_stat(s, "TFT17_Gnar", "ad", "MeepPercentBAD", base_stats_map=m),      
    },
    "Fizz": { 
        "ModifiedDamage": lambda s, m: s.get("DashDamage", 0),
        "ModifiedChompDamage": lambda s, m: s.get("BiteDamageAP", "BiteDamageMeep"),
        "ModifiedNumMeeps": lambda s, m: s.get("MeepsPerAstro", 0),
        "ModifiedMeepBonusDamage": lambda s, m: s.get("BiteDamageMeep", 0), 
    },
    "Fiora": { 
        "ModifiedHealing": lambda s, m: s.get("AuraHealing", 0),
    },
    "Rammus": { 
        "ModifiedShield": lambda s, m: s.get("ShieldAP", 0),
        "ModifiedDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Rammus", "armor", "DamageArmor", base_stats_map=m, add_key="DamageAP"
        ),
        "ModifiedFlatDR": lambda s, m: s.get("FlatDRPerMeep", 0),
        "ModifiedPassiveDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Rammus", "armor", "PassivePercentArmor", base_stats_map=m
        ),
    },
    "Poppy": { 
        "ModifiedNumMeeps": lambda s, m: s.get("MeepsPerAstro", 0),
    },
    "Corki": { 
        "ModifiedDamage": lambda s, m: sum_stats(s, ["MissileAD", "MissileAP"]),
        "ModifiedProcDamage": lambda s, m: sum_and_scale(s, ["MissileAD", "MissileAP"], "ProcDamageMult"),
        "ModifiedMeepCooldown": lambda s, m: s.get("BaseMeepCooldown", 0),
    },
    "Veigar": { 
        "ModifiedMiniMeeps": lambda s, m: s.get("MiniMeepsPerAstro", 0),
    },
    "Caitlyn": { 
        "ModifiedHeadshotDamage": lambda s, m: s.get("Damage", "BonusDamage"),
        "ModifiedNovaHeadshotDamage": lambda s, m: sum_and_scale(s, ["Damage", "BonusDamage"], "NovaHeadshotModifier"),
    },
    "Maokai": { 
        "ModifiedNovaDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Maokai", "hp", "NovaHealthDamage", base_stats_map=m
        )
    },
    "Kindred": { 
        "ModifiedDamage": lambda s, m: s.get("SpellDamage", 0),
    },
    "Urgot": { 
        "ShotgunRange": lambda s, m: 2,
        "ModifiedShield": lambda s, m: s.get("ShieldAmount", 0),
    },
    "Aurelion Sol": { 
        "ModifiedDamage": lambda s, m: s.get("DamagePerSecond", 0),
    },
    "The Mighty Mech": { 
        "ModifiedDamage": lambda s, m: [
            round(s.get("ARMARScaling", [0,0,0])[i] * (m["TFT17_Galio"]["armor"] + m["TFT17_Galio"]["mr"]))
            for i in range(3)
        ]
    },
    "Pyke": { 
        "ModifiedDamage": lambda s, m: s.get("SpearDamage", 0),
        "ModifiedAreaDamage": lambda s, m: s.get("AoEDamage", 0),
    },
    "Gragas": { 
        "Duration": lambda s, m: s.get("DURATION", 0),
        "ModifiedHeal": lambda s, m: scale_by_base_stat(
            s, "TFT17_Gragas", "hp", "HealingPercentHealth", base_stats_map=m, add_key="HEALING"
        )
    },
    "Nasus": { 
        "ModifiedDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Nasus", "hp", "DamageHealth", base_stats_map=m, add_key="DamageAP"
        )
    },
    "Samira": { 
        "ModifiedPassiveDamage": lambda s, m: sum_stats(s, ["PassiveAD", "PassiveAP"]),
    },
    "Talon": { 
        "ModifiedBleedDamage": lambda s, m: sum_stats(s, ["ADBleedDamage", "APBleedDamage"]),
    },
    "Master Yi": { 
        "ModifiedDamage": lambda s, m: sum_stats(s, ["DamageAD", "DamageAP"]),
    },
    "Jax": { 
        "ModifiedShield": lambda s, m: s.get("ShieldAP", 0),
        "ModifiedDamage": lambda s, m: [
            round(s.get("ArmorMRScale", [0,0,0])[i] * (m["TFT17_Jax"]["armor"] + m["TFT17_Jax"]["mr"]))
            for i in range(3)
        ]
    },
    "Riven": { 
        "ModifiedPassiveADDamage": lambda s, m: s.get("PassiveDamage", 0),
        "ModifiedPassiveAPDamage": lambda s, m: s.get("PassiveDamage", 0),
        "ModifiedADDamage": lambda s, m: s.get("Damage", 0),
        "ModifiedAPDamage": lambda s, m: s.get("Damage", 0),
        "ModifiedAPWaveDamage": lambda s, m: s.get("WaveDamage", 0),
        "ModifiedADWaveDamage": lambda s, m: s.get("WaveDamage", 0),
    },
    "Shen": { 
        "ModifiedBonusDamage": lambda s, m: s.get("BonusDamageOnAttack", 0),
        "ModifiedShield": lambda s, m: scale_by_base_stat(
            s, "TFT17_Shen", "hp", "ShieldHP", base_stats_map=m, add_key="ShieldAP"
        )
    },
    "Leona": { 
        "ModifiedShield": lambda s, m: s.get("ShieldAmount", 0),
    },
    "Diana": { 
        "ModifiedDamage": lambda s, m: s.get("BaseDamage", 0),
    },
    "LeBlanc": { 
        "ModifiedBaseAttackDamage": lambda s, m: s.get("BasicAttackDamage", 0),
    },
    "Cho'Gath": { 
        "TotalDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Chogath", "hp", "PercentMaximumHealthDamage", base_stats_map=m, add_key="BonusDamage"
        )
    },
    "Meepsie": { 
        "ModifiedHeal": lambda s, m: scale_by_base_stat(
            s, "TFT17_IvernMinion", "hp", "HealingPercentHealth", base_stats_map=m, add_key="HealingAP"
        ),
        "ModifiedHealingAndShielding": lambda s, m: [
            f"{clean_num(v * 100)}%" for v in (s.get("HealingAndShieldingPerAstro") or [0, 0, 0])
        ],
    },
    "Graves": { 
        "ModifiedSecondaryDamage": lambda s, m: sum_stats(s, ["SecondaryDamageAD", "SecondaryDamageAP"]),
        "ModifiedPassiveDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_Graves", "ad", "PassivePercentBAD", base_stats_map=m
        )
    },
    "Tahm Kench": { 
        "ModifiedHeal": lambda s, m: scale_by_base_stat(
            s, "TFT17_TahmKench", "hp", "HealHP", base_stats_map=m, add_key="HealAP"
        ),
        "ModifiedDamage": lambda s, m: scale_by_base_stat(
            s, "TFT17_TahmKench", "hp", "DamageHP", base_stats_map=m, add_key="DamageAP"
        )
    },
    "Rhaast": { 
        "ModifiedHeal": lambda s, m: s.get("HealAmount", 0),
    },
    "Rek'Sai": { 
        "TotalHealing": lambda s, m: scale_by_base_stat(
            s, "TFT17_RekSai", "hp", "PercentMaximumHealthHealing", base_stats_map=m, add_key="APHealing"
        ),
    },
    "Pantheon": { 
        "ModifiedShield": lambda s, m: scale_by_base_stat(
            s, "TFT17_Pantheon", "hp", "PercentHealthShield", base_stats_map=m, add_key="APShield"
        ),
        "ModifiedDamage": lambda s, m: s.get("TrueDamagePerSecond", 0),
    },
    "Morgana": { 
        "ModifiedDamagePerSecond": lambda s, m: s.get("TetherDamagePerSecond", 0),
    },
}

GLOBAL_EXCEPTIONS = {
    "TotalDamage": lambda s, m: sum_stats(s, ["ADDamage", "APDamage"]),
    "DamageTotal": lambda s, m: s.get("Damage", 0),
    "ModifiedNumMeeps": lambda s, m: s.get("NumMeepsPerAstro", 0),
}