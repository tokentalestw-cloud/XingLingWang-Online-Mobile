import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

extra_cards = [c for c in cards if c.get('deck_eligible') is False]
for c in extra_cards:
    print(f"ID: {c['id']}, Name: {c['name']}")
    print(f"  Faction: {json.dumps(c.get('faction'), ensure_ascii=False)}")
    print(f"  Race: {json.dumps(c.get('race'), ensure_ascii=False)}")
    print(f"  Deck: {json.dumps(c.get('deck'), ensure_ascii=False)}")
