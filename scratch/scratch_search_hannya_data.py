import json
import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
cards_path = os.path.join(base_dir, "data/cards.json")

results = []
if os.path.exists(cards_path):
    with open(cards_path, "r", encoding="utf-8") as f:
        try:
            cards = json.load(f)
            print("Total cards in data/cards.json:", len(cards))
            for card in cards:
                if any(x in card.get("name", "") for x in ["般若", "Prajna", "Hannya"]):
                    results.append(card)
        except Exception as e:
            print("Error reading cards.json:", e)

# Write results
out_path = os.path.join(base_dir, "scratch/hannya_card_info.json")
with open(out_path, "w", encoding="utf-8") as out_f:
    json.dump(results, out_f, ensure_ascii=False, indent=2)

print(f"Done. Found {len(results)} matching cards. Saved to scratch/hannya_card_info.json")
