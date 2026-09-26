import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

deck_cards = decks.get('妖精', decks.get('妖精_預組', []))
total_mana = 0
for cid in deck_cards:
    card = next((c for c in cards if c.get('id') == cid), None)
    if card:
        mana = int(card.get('mana', 0))
        total_mana += mana
        print(f"{cid} ({card.get('name')}): {mana} mana")
    else:
        print(f"{cid}: NOT FOUND")
print(f"Total Mana: {total_mana}")
