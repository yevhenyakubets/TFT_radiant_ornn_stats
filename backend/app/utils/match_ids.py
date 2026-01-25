import json
from pathlib import Path

MATCH_IDS_FILE = Path(__file__).resolve().parents[2] / "20 matchids.txt"

def load_match_ids() -> list[str]:
    with open(MATCH_IDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)