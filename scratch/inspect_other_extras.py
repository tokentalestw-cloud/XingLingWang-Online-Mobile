import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)

extra_decks = ['獸人_extra', '妖怪村莊_extra', '藝術品_extra']
for deck_name in extra_decks:
    print(f"\n=== {deck_name} ===")
    card_ids = decks.get(deck_name, [])
    for cid in card_ids:
        # find in cards list (cards is a list of card objects)
        found = False
        for c in cards:
            if c.get('id') == cid:
                print(f"  ID: {cid}, Name: {c.get('name')}, Type: {c.get('type')}")
                print(f"    Effect: {c.get('effect_text')}")
                found = True
                break
        if not found:
            print(f"  ID: {cid} not found in cards.json")
