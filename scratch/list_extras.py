import json
with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)
extra_cards = [c for c in cards if c.get('deck_eligible') is False]
print('Total extra cards:', len(extra_cards))
for c in extra_cards:
    print(f"{c['id']}: {c['name']} (faction: {c.get('faction')}, race: {c.get('race')}, deck: {c.get('deck')})")
