import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

cards_path = r"data/cards.json"
with open(cards_path, 'r', encoding='utf-8') as f:
    cards = json.load(f)

target_ids = [
    "NMG-0001", "R-NMG-0001", 
    "NMG-0010", "R-NMG-0010", "SSR-NMG-0010",
    "R-NMG-0027", "R-NMG-0028", "R-NMG-0038",
    "R-NMS-0048", "SSSR-NMS-0046", "SSSR-NMS-0050",
    "SSSR-NMS-0051", "SSSR-NMS-0055"
]

for card in cards:
    if card['id'] in target_ids:
        print(f"ID: {card['id']} | Name: {card['name']} | Type: {card.get('type')} | Faction: {card.get('faction') or card.get('deck')} | Effect: {card.get('effect_text') or card.get('effect')}")
