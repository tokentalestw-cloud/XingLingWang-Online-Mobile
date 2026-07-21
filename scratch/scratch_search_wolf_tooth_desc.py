import json
import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
cards_path = os.path.join(base_dir, "data/cards.json")

if os.path.exists(cards_path):
    with open(cards_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
        for c in cards:
            if "狼牙棒" in c.get("name", "") or c.get("id") == "R-ORC-0054":
                print(json.dumps(c, ensure_ascii=False, indent=2))
