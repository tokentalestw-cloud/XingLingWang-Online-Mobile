import json
import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

# Load scratch_cards.json
cards_path = os.path.join(base_dir, "scratch_cards.json")
if os.path.exists(cards_path):
    with open(cards_path, "r", encoding="utf-8") as f:
        try:
            cards = json.load(f)
            print("=== scratch_cards.json ===")
            for card in cards:
                if any(x in card.get("name", "") for x in ["般若", "Prajna", "Hannya"]):
                    print(json.dumps(card, ensure_ascii=False, indent=2))
        except Exception as e:
            print("Error loading scratch_cards.json:", e)

# Also check static/decks.json
decks_path = os.path.join(base_dir, "static/decks.json")
if os.path.exists(decks_path):
    with open(decks_path, "r", encoding="utf-8") as f:
        try:
            decks = json.load(f)
            print("=== static/decks.json ===")
            # Look inside decks
            for deck_name, deck_data in decks.items():
                print(f"Deck: {deck_name}")
                for card in deck_data.get("cards", []):
                    if any(x in card.get("name", "") for x in ["般若", "Prajna", "Hannya"]):
                        print(json.dumps(card, ensure_ascii=False, indent=2))
                for card in deck_data.get("extraDeck", []):
                    if any(x in card.get("name", "") for x in ["般若", "Prajna", "Hannya"]):
                        print(json.dumps(card, ensure_ascii=False, indent=2))
        except Exception as e:
            print("Error loading static/decks.json:", e)
