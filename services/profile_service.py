import json
from pathlib import Path


def load_profile():
    path = Path("data/profile.json")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)