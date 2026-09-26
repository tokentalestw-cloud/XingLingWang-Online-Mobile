import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for deck_name in ['獸人', '藝術品']:
    deck_cards = decks.get(deck_name, [])
    print(f"\n--- {deck_name} ---")
    for cid in deck_cards:
        card = next((c for c in cards if c.get('id') == cid), None)
        if card:
            t = card.get('type', '')
            m = card.get('mana', 0)
            n = card.get('name', '')
            print(f"{cid} ({n}) [Type: {t}]: {m} mana")
