from app.data.radiant_items import CHAMPIONS_BY_ROLE

ARTIFACT_ITEMS = [
    "TFT_Item_Artifact_AegisOfDawn",
    "TFT_Item_Artifact_AegisOfDusk",
    "TFT_Item_Artifact_BlightingJewel",
    "TFT_Item_Artifact_CappaJuice",
    "TFT_Item_Artifact_Dawncore",
    "TFT_Item_Artifact_EternalPact",
    "TFT_Item_Artifact_Fishbones",
    "TFT_Item_Artifact_HellfireHatchet",
    "TFT_Item_Artifact_HorizonFocus",
    "TFT_Item_Artifact_LichBane",
    "TFT_Item_Artifact_LightshieldCrest",
    "TFT_Item_Artifact_LudensTempest",
    "TFT_Item_Artifact_Mittens",
    "TFT_Item_Artifact_NavoriFlickerblades",
    "TFT_Item_Artifact_ProwlersClaw",
    "TFT_Item_Artifact_RapidFirecannon",
    "TFT_Item_Artifact_SeekersArmguard",
    "TFT_Item_Artifact_SilvermereDawn",
    "TFT_Item_Artifact_StatikkShiv",
    "TFT_Item_Artifact_TalismanOfAscension",
    "TFT_Item_Artifact_TheIndomitable",
    "TFT_Item_Artifact_TitanicHydra",
    "TFT_Item_Artifact_VoidGauntlet",
    "TFT_Item_Artifact_WitsEnd",

    # Ornn / special artifacts (no TFT_Item_Artifact prefix)
    "TFT4_Item_OrnnDeathsDefiance",
    "TFT4_Item_OrnnInfinityForce",
    "TFT4_Item_OrnnTheCollector",
    "TFT4_Item_OrnnZhonyasParadox",

    "TFT7_Item_ShimmerscaleGamblersBlade",
    "TFT7_Item_ShimmerscaleMogulsMail",

    "TFT9_Item_OrnnHorizonFocus",
    "TFT9_Item_OrnnHullbreaker",

    # Darkin items (still artifacts)
    "TFT16_TheDarkinAegis",
    "TFT16_TheDarkinBow",
    "TFT16_TheDarkinScythe",
    "TFT16_TheDarkinStaff",
]



ARTIFACTS_BY_ROLE = {
    "tank": [
        "TFT_Item_Artifact_AegisOfDawn",
        "TFT_Item_Artifact_AegisOfDusk",
        "TFT_Item_Artifact_HorizonFocus",
        "TFT_Item_Artifact_LightshieldCrest",
        "TFT_Item_Artifact_SeekersArmguard",
        "TFT_Item_Artifact_SilvermereDawn",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT_Item_Artifact_TheIndomitable",
        "TFT_Item_Artifact_TitanicHydra",
        "TFT_Item_Artifact_VoidGauntlet",
        "TFT4_Item_OrnnInfinityForce",
        "TFT7_Item_ShimmerscaleMogulsMail",
        "TFT9_Item_OrnnHullbreaker",
        "TFT16_TheDarkinAegis",

    ],
    "ad caster": [
        "TFT_Item_Artifact_CappaJuice",
        "TFT_Item_Artifact_Dawncore",
        "TFT_Item_Artifact_Fishbones",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnTheCollector",
        "TFT7_Item_ShimmerscaleGamblersBlade",
        "TFT9_Item_OrnnHorizonFocus",
    ],
    "ad fighter": [
        "TFT_Item_Artifact_CappaJuice",
        "TFT_Item_Artifact_Dawncore",
        "TFT_Item_Artifact_Fishbones",
        "TFT_Item_Artifact_HellfireHatchet",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_Mittens",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_ProwlersClaw",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_SeekersArmguard",
        "TFT_Item_Artifact_SilvermereDawn",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT_Item_Artifact_TitanicHydra",
        "TFT4_Item_OrnnDeathsDefiance",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnTheCollector",
        "TFT9_Item_OrnnHorizonFocus",
        "TFT9_Item_OrnnHullbreaker",
        "TFT16_TheDarkinBow",
        "TFT16_TheDarkinScythe",
    ],
    "ad aa": [
        "TFT_Item_Artifact_CappaJuice",
        "TFT_Item_Artifact_Fishbones",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_StatikkShiv",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT_Item_Artifact_TitanicHydra",
        "TFT_Item_Artifact_WitsEnd",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnTheCollector",
        "TFT7_Item_ShimmerscaleGamblersBlade",
        "TFT9_Item_OrnnHorizonFocus",
        "TFT16_TheDarkinBow",
    ],
    "ap caster": [
        "TFT_Item_Artifact_BlightingJewel",
        "TFT_Item_Artifact_Dawncore",
        "TFT_Item_Artifact_EternalPact",
        "TFT_Item_Artifact_HorizonFocus",
        "TFT_Item_Artifact_LichBane",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnZhonyasParadox",
        "TFT7_Item_ShimmerscaleGamblersBlade",
        "TFT9_Item_OrnnHorizonFocus",
        "TFT16_TheDarkinStaff",
    ],
    "ap fighter": [
        "TFT_Item_Artifact_BlightingJewel",
        "TFT_Item_Artifact_Dawncore",
        "TFT_Item_Artifact_EternalPact",
        "TFT_Item_Artifact_HorizonFocus",
        "TFT_Item_Artifact_HellfireHatchet",
        "TFT_Item_Artifact_LichBane",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_Mittens",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_SeekersArmguard",
        "TFT_Item_Artifact_SilvermereDawn",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT_Item_Artifact_WitsEnd",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnZhonyasParadox",
        "TFT7_Item_ShimmerscaleGamblersBlade",
        "TFT9_Item_OrnnHorizonFocus",
        "TFT9_Item_OrnnHullbreaker",
        "TFT16_TheDarkinScythe",
        "TFT16_TheDarkinStaff",
    ],
    "ap aa": [
        "TFT_Item_Artifact_CappaJuice",
        "TFT_Item_Artifact_Fishbones",
        "TFT_Item_Artifact_LichBane",
        "TFT_Item_Artifact_LudensTempest",
        "TFT_Item_Artifact_NavoriFlickerblades",
        "TFT_Item_Artifact_RapidFirecannon",
        "TFT_Item_Artifact_StatikkShiv",
        "TFT_Item_Artifact_TalismanOfAscension",
        "TFT_Item_Artifact_WitsEnd",
        "TFT4_Item_OrnnInfinityForce",
        "TFT4_Item_OrnnZhonyasParadox",
        "TFT7_Item_ShimmerscaleGamblersBlade",
        "TFT9_Item_OrnnHorizonFocus",
    ],
}

CHAMPION_ARTIFACTS = {}

for role, champions in CHAMPIONS_BY_ROLE.items():
    items_for_role = ARTIFACTS_BY_ROLE[role]

    for champ in champions:
        if champ not in CHAMPION_ARTIFACTS:
            CHAMPION_ARTIFACTS[champ] = []

        CHAMPION_ARTIFACTS[champ].extend(items_for_role)

# optional but recommended: remove duplicates
for champ in CHAMPION_ARTIFACTS:
    CHAMPION_ARTIFACTS[champ] = list(set(CHAMPION_ARTIFACTS[champ]))
CHAMPION_ARTIFACTS["TFT16_Ornn"] = ARTIFACT_ITEMS.copy()