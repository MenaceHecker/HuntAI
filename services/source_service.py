import json
from pathlib import Path


def load_sources():
    path = Path("data/job_sources.json")
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)