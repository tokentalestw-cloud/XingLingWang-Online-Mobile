import json
import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
cards_path = os.path.join(base_dir, "scratch_cards.json")

if os.path.exists(cards_path):
    with open(cards_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
        print("Total cards:", len(cards))
        names = [c.get("name", "") for c in cards]
        print("First 50 card names:")
        for name in sorted(names)[:50]:
            print(f"- {name}")
        
        # Search for any card name that contains any character of "般若"
        print("\nSearch results for '般若':")
        for c in cards:
            if "般" in c.get("name", "") or "若" in c.get("name", "") or "hannya" in c.get("name", "").lower() or "prajna" in c.get("name", "").lower():
                print(json.dumps(c, ensure_ascii=False, indent=2))
else:
    print("scratch_cards.json does not exist")
