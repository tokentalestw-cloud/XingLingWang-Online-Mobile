import json
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for c in cards:
    if '般若' in c['name']:
        print(f"ID: {c['id']}")
        print(f"Name: {c['name']}")
        print(f"Faction: {c.get('faction')}")
        print(f"Type: {c.get('type')}")
        print(f"Effect: {json.dumps(c.get('effect_text'), ensure_ascii=False)}")
        print("-" * 40)
