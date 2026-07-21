import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

cards_path = r"data/cards.json"
with open(cards_path, 'r', encoding='utf-8') as f:
    cards = json.load(f)

for card in cards:
    if "鬧鐘" in card['name']:
        print(f"ID: {card['id']} | Name: {card['name']} | Type: {card.get('type')} | Faction: {card.get('faction') or card.get('deck')} | Effect: {card.get('effect_text') or card.get('effect')}")
