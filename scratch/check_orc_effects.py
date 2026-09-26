import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

orc_cards = decks.get('獸人', [])
for cid in orc_cards:
    card = next((c for c in cards if c.get('id') == cid), None)
    if card:
        print(f"{cid} ({card.get('name')}): {card.get('effect_text')}")
