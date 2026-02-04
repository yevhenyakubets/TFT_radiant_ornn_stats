import json
from pathlib import Path

exceptions = {
    "TFT16_TheDarkinStaff",
    "TFT16_TheDarkinBow",
    "TFT16_TheDarkinScythe",
    "TFT16_TheDarkinAegis",
    "TFT7_Item_ShimmerscaleGamblersBlade",
    "TFT7_Item_ShimmerscaleMogulsMail",
}

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

ITEM_JSON_PATH = Path(__file__).parent / "tft-item.json"

with open(ITEM_JSON_PATH, encoding="utf-8") as f:
    raw = json.load(f)

ARTIFACT_ITEMS: dict[str, dict] = {}

def is_artifact_item(item_id: str) -> bool:
    return (
        "Ornn" in item_id
        or "Artifact" in item_id
        or item_id in exceptions
    )


# build artifact items
for entry in raw["data"].values():
    item_id = entry["id"]

    if not is_artifact_item(item_id):
        continue

    ARTIFACT_ITEMS[item_id] = {
        "id": item_id,
        "name": entry["name"],
        "image": entry["image"]["full"],
        "roles": []
    }

# layer roles
for role, items in ARTIFACTS_BY_ROLE.items():
    for item_id in items:
        if item_id in ARTIFACT_ITEMS:
            ARTIFACT_ITEMS[item_id]["roles"].append(role)

# remove artifacts with no assigned roles
ARTIFACT_ITEMS = {
    item_id: data
    for item_id, data in ARTIFACT_ITEMS.items()
    if data["roles"]
}

def get_all_artifact_items() -> dict[str, dict]:
    return ARTIFACT_ITEMS