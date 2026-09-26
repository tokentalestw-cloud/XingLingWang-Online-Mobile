import json
import codecs

with codecs.open('static/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
fairy_deck = decks.get('妖精_妖精預組', [])

with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

out = '--- Fairy Deck Cards ---\n'
for c in cards:
    if c['id'] in fairy_deck:
        effect = c.get('effect_text', 'N/A')
        out += f"ID: {c['id']}\nName: {c['name']}\nEffect: {effect}\n\n"

with codecs.open('scratch/fairy_effects.md', 'w', encoding='utf-8') as f:
    f.write(out)
