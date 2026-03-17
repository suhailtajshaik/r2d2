#!/usr/bin/env python3
"""
Generate /home/r2d2/newspapers/index.json
Lists all available editions, newest first.
Run after every Maxwell newspaper generation.
"""
import json
import os
from pathlib import Path

NEWSPAPERS_DIR = Path("/home/r2d2/newspapers")
OUTPUT = NEWSPAPERS_DIR / "index.json"

editions = []

for data_file in sorted(NEWSPAPERS_DIR.glob("*/*/*/data.json"), reverse=True):
    try:
        with open(data_file) as f:
            d = json.load(f)
        date = d.get("date", "")
        label = d.get("label", "")
        if not date:
            continue
        
        y, m, day = date.split("-")
        entry = {
            "date": date,
            "label": label,
        }
        # Check for optional files
        base = data_file.parent
        if (base / "headlines-today.pdf").exists():
            entry["pdf"] = f"/archive/{y}/{m}/{day}/headlines-today.pdf"
        if (base / "headlines-today.mp3").exists():
            entry["audio"] = f"/archive/{y}/{m}/{day}/headlines-today.mp3"
        
        editions.append(entry)
    except Exception as e:
        print(f"Skipping {data_file}: {e}")

index = {"editions": editions}

with open(OUTPUT, "w") as f:
    json.dump(index, f, indent=2)

print(f"Generated index.json with {len(editions)} editions:")
for e in editions:
    print(f"  {e['date']} — {e['label']}")
