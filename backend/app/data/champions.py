import json
from pathlib import Path
from app.data.artifacts import ARTIFACTS_BY_ROLE
from app.data.radiant_items import RADIANT_ITEMS_BY_ROLE

CHAMPIONS_BY_ROLE = {
    "tank": [
        "TFT16_Blitzcrank",
        "TFT16_Illaoi",
        "TFT16_JarvanIV",
        "TFT16_Rumble",
        "TFT16_Shen",
        "TFT16_ChoGath",
        "TFT16_Neeko",
        "TFT16_Poppy",
        "TFT16_Sion",
        "TFT16_Vi",
        "TFT16_XinZhao",
        "TFT16_Yorick",
        "TFT16_Darius",
        "TFT16_DrMundo",
        "TFT16_Kennen",
        "TFT16_Kobuko",
        "TFT16_Leona",
        "TFT16_Loris",
        "TFT16_Nautilus",
        "TFT16_Sejuani",
        "TFT16_Braum",
        "TFT16_Garen",
        "TFT16_Nasus",
        "TFT16_RiftHerald",
        "TFT16_Singed",
        "TFT16_Skarner",
        "TFT16_Swain",
        "TFT16_Taric",
        "TFT16_Wukong",
        "TFT16_Galio",
        "TFT16_Ornn",
        "TFT16_Shyvana",
        "TFT16_TahmKench",
        "TFT16_Thresh",
    ],
    "ad caster": [
        "TFT16_Caitlyn",
        "TFT16_Ashe",
        "TFT16_Tristana",
        "TFT16_Kaisa",
        "TFT16_Kalista",
        "TFT16_MissFortune",
        "TFT16_Kindred",
        "TFT16_Lucian",
    ],
    "ad fighter": [
        "TFT16_Briar",
        "TFT16_Illaoi",
        "TFT16_Qiyana",
        "TFT16_Viego",
        "TFT16_Graves",
        "TFT16_RekSai",
        "TFT16_Tryndamere",
        "TFT16_Vi",
        "TFT16_Yasuo",
        "TFT16_Darius",
        "TFT16_Gangplank",
        "TFT16_Ambessa",
        "TFT16_BelVeth",
        "TFT16_Renekton",
        "TFT16_Warwick",
        "TFT16_Yone",
        "TFT16_Aatrox",
        "TFT16_Shyvana",
        "TFT16_THex",
        "TFT16_Volibear",
        "TFT16_Brock",
        "TFT16_Zaahen",
        "TFT16_BaronNashor",
    ],
    "ad aa": [
        "TFT16_Jhin",
        "TFT16_Aphelios",
        "TFT16_Ashe",
        "TFT16_Draven",
        "TFT16_Jinx",
        "TFT16_Vayne",
        "TFT16_BelVeth",
        "TFT16_Yunara",
        "TFT16_Kindred",
    ],
    "ap caster": [
        "TFT16_Anivia",
        "TFT16_KogMaw",
        "TFT16_Lulu",
        "TFT16_Sona",
        "TFT16_Bard",
        "TFT16_Orianna",
        "TFT16_Teemo",
        "TFT16_Ahri",
        "TFT16_Leblanc",
        "TFT16_Malzahar",
        "TFT16_Milio",
        "TFT16_Zoe",
        "TFT16_Seraphine",
        "TFT16_Lissandra",
        "TFT16_Lux",
        "TFT16_Veigar",
        "TFT16_Annie",
        "TFT16_Azir",
        "TFT16_Mel",
        "TFT16_Xerath",
        "TFT16_Ziggs",
        "TFT16_Zilean",
        "TFT16_AurelionSol",
        "TFT16_Ryze",

    ],
    "ap fighter": [
        "TFT16_Viego",
        "TFT16_Ekko",
        "TFT16_Gwen",
        "TFT16_Diana",
        "TFT16_Fizz",
        "TFT16_Singed",
        "TFT16_Nidalee",
        "TFT16_Fiddlesticks",
        "TFT16_Galio",
        "TFT16_Sett",
        "TFT16_TahmKench",
        "TFT16_Thresh",
        "TFT16_Sylas",
    ],
    "ap aa": [
        "TFT16_KogMaw",
        "TFT16_TwistedFate",
        "TFT16_Kaisa",
        "TFT16_Azir",
        "TFT16_Rumble",
    ],
}

CHAMPION_JSON_PATH = Path(__file__).parent / "tft-champion.json"

with open(CHAMPION_JSON_PATH, encoding="utf-8") as f:
    raw = json.load(f)

champions: dict[str, dict] = {}

for entry in raw["data"].values():
    champ_id = entry["id"]

    if not champ_id.startswith("TFT16_"):
        continue

    champions[champ_id] = {
        "id": champ_id,
        "name": entry["name"],
        "cost": entry["cost"],
        "image": entry["image"]["full"],
        "roles": []
    }



for role, champ_list in CHAMPIONS_BY_ROLE.items():
    for champ_id in champ_list:
        if champ_id in champions:
            champions[champ_id]["roles"].append(role)



def get_champion_roles(champion: str) -> list[str]:
    return champions.get(champion, {}).get("roles", [])

def get_all_champions() -> dict[str, dict]:
    return champions

def get_allowed_radiant_items(roles: list[str]) -> set[str]:
    """Returns a set of all Radiant items suitable for the given roles."""
    allowed = set()
    for role in roles:
        if role in RADIANT_ITEMS_BY_ROLE:
            allowed.update(RADIANT_ITEMS_BY_ROLE[role])
    return allowed

def get_allowed_artifact_items(roles: list[str]) -> set[str]:
    """Returns a set of all Artifact items suitable for the given roles."""
    allowed = set()
    for role in roles:
        if role in ARTIFACTS_BY_ROLE:
            allowed.update(ARTIFACTS_BY_ROLE[role])
    return allowed