from collections import defaultdict
from app.data.radiant_items import CHAMPIONS_BY_ROLE

CHAMPIONS = {}

for role, champions in CHAMPIONS_BY_ROLE.items():
    for champ in champions:
        if champ not in CHAMPIONS:
            CHAMPIONS[champ] = {
                "id": champ,
                "name": champ.replace("TFT16_", ""),
                "roles": []
            }

        CHAMPIONS[champ]["roles"].append(role)
