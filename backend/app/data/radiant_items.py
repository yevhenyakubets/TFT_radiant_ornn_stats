import json
from pathlib import Path

RADIANT_ITEMS_BY_ROLE = {
    "tank": [
        "TFT5_Item_AdaptiveHelmRadiant",
        "TFT5_Item_BrambleVestRadiant",
        "TFT5_Item_FrozenHeartRadiant",
        "TFT5_Item_GargoyleStoneplateRadiant",
        "TFT5_Item_SteraksGageRadiant",
        "TFT5_Item_SunfireCapeRadiant",
        "TFT5_Item_WarmogsArmorRadiant",
        "TFT5_Item_CrownguardRadiant",
        "TFT5_Item_DragonsClawRadiant",
        "TFT5_Item_IonicSparkRadiant",
        "TFT5_Item_NightHarvesterRadiant",
        "TFT5_Item_RedemptionRadiant",
        "TFT5_Item_SpectralGauntletRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
    ],
    "ad caster": [
        "TFT5_Item_AdaptiveHelmRadiant",
        "TFT5_Item_DeathbladeRadiant",
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_InfinityEdgeRadiant",
        "TFT5_Item_LastWhisperRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_BlueBuffRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_QuicksilverRadiant",
        "TFT5_Item_RunaansHurricaneRadiant",
        "TFT5_Item_SpearOfShojinRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",

    ],
    "ad fighter": [
        "TFT5_Item_DeathbladeRadiant",
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_InfinityEdgeRadiant",
        "TFT5_Item_LastWhisperRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_BlueBuffRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_QuicksilverRadiant",
        "TFT5_Item_RunaansHurricaneRadiant",
        "TFT5_Item_SpearOfShojinRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
        "TFT5_Item_BloodthirsterRadiant",
        "TFT5_Item_GuardianAngelRadiant",
        "TFT5_Item_SteraksGageRadiant",
        "TFT5_Item_TitansResolveRadiant",
    ],
    "ad aa": [
        "TFT5_Item_DeathbladeRadiant",
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_InfinityEdgeRadiant",
        "TFT5_Item_LastWhisperRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_QuicksilverRadiant",
        "TFT5_Item_RunaansHurricaneRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
        "TFT5_Item_TitansResolveRadiant",

    ],
    "ap caster": [
        "TFT5_Item_AdaptiveHelmRadiant",
        "TFT5_Item_ArchangelsStaffRadiant",
        "TFT5_Item_BlueBuffRadiant",
        "TFT5_Item_CrownguardRadiant",
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_JeweledGauntletRadiant",
        "TFT5_Item_MorellonomiconRadiant",
        "TFT5_Item_RabadonsDeathcapRadiant",
        "TFT5_Item_SpearOfShojinRadiant",
        "TFT5_Item_StatikkShivRadiant",
        "TFT5_Item_LeviathanRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
    ],
    "ap fighter": [
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_BlueBuffRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_QuicksilverRadiant",
        "TFT5_Item_SpearOfShojinRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
        "TFT5_Item_BloodthirsterRadiant",
        "TFT5_Item_GuardianAngelRadiant",
        "TFT5_Item_SteraksGageRadiant",
        "TFT5_Item_TitansResolveRadiant",
        "TFT5_Item_AdaptiveHelmRadiant",
        "TFT5_Item_ArchangelsStaffRadiant",
        "TFT5_Item_CrownguardRadiant",
        "TFT5_Item_StatikkShivRadiant",
        "TFT5_Item_LeviathanRadiant",
        "TFT5_Item_JeweledGauntletRadiant",
        "TFT5_Item_MorellonomiconRadiant",
        "TFT5_Item_RabadonsDeathcapRadiant",
    ],
    "ap aa": [
        "TFT5_Item_ArchangelsStaffRadiant",
        "TFT5_Item_GiantSlayerRadiant",
        "TFT5_Item_RapidFirecannonRadiant",
        "TFT5_Item_GuinsoosRagebladeRadiant",
        "TFT5_Item_HandOfJusticeRadiant",
        "TFT5_Item_HextechGunbladeRadiant",
        "TFT5_Item_QuicksilverRadiant",
        "TFT5_Item_TrapClawRadiant",
        "TFT5_Item_ThiefsGlovesRadiant",
        "TFT5_Item_TitansResolveRadiant",
        "TFT5_Item_JeweledGauntletRadiant",
        "TFT5_Item_MorellonomiconRadiant",
        "TFT5_Item_RabadonsDeathcapRadiant",
        "TFT5_Item_StatikkShivRadiant",
    ],
}

ITEM_JSON_PATH = Path(__file__).parent / "tft-item.json"

with open(ITEM_JSON_PATH, encoding="utf-8") as f:
    raw = json.load(f)

RADIANT_ITEMS: dict[str, dict] = {}

def is_radiant_item(item_id: str) -> bool:
    return "Radiant" in item_id

# build all radiant items
for entry in raw["data"].values():
    item_id = entry["id"]

    if not is_radiant_item(item_id):
        continue

    RADIANT_ITEMS[item_id] = {
        "id": item_id,
        "name": entry["name"],
        "image": entry["image"]["full"],
        "roles": []
    }

# layer roles
for role, items in RADIANT_ITEMS_BY_ROLE.items():
    for item_id in items:
        if item_id in RADIANT_ITEMS:
            RADIANT_ITEMS[item_id]["roles"].append(role)

# remove artifacts with no assigned roles
RADIANT_ITEMS = {
    item_id: data
    for item_id, data in RADIANT_ITEMS.items()
    if data["roles"]
}


def get_all_radiant_items() -> dict[str, dict]:
    return RADIANT_ITEMS

print(len(RADIANT_ITEMS))