import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for deck_name in decks:
    if '獸人' in deck_name or '藝術' in deck_name:
        deck_cards = decks[deck_name]
        total_mana = 0
        mana_details = []
        for cid in deck_cards:
            card = next((c for c in cards if c.get('id') == cid), None)
            if card:
                mana = int(card.get('mana', 0))
                total_mana += mana
                if mana > 0:
                    mana_details.append(f"{cid} ({card.get('name')}): {mana}")
            else:
                mana_details.append(f"{cid}: NOT FOUND")
        print(f"Deck: {deck_name}, Total Mana: {total_mana}")
        for d in mana_details:
            print("  " + d)
