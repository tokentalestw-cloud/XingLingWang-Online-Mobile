import json
import codecs
import re

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    game_js = f.read()

orc_cards = decks.get('獸人', [])

unimplemented = []
implemented = []

for cid in orc_cards:
    card = next((c for c in cards if c.get('id') == cid), None)
    if not card: continue
    
    # Check if the ID or the Name appears in the JS code
    id_clean = cid.replace('-2', '').replace(' ', '')
    name = card.get('name', '').replace(' ', '')
    
    found = False
    
    if id_clean in game_js:
        found = True
    elif name and len(name) > 2 and name in game_js:
        found = True
        
    if not found:
        # Also check for alternate spellings or typos like 0RC instead of ORC
        if 'ORC-' in id_clean and id_clean.replace('ORC-', '0RC-') in game_js:
            found = True
        elif 'ORC--' in id_clean and id_clean.replace('ORC--', 'ORC-') in game_js:
            found = True
            
    if found:
        implemented.append(f"{cid} ({card.get('name')})")
    else:
        unimplemented.append(f"{cid} ({card.get('name')})")

print("--- Implemented? ---")
for x in implemented:
    print("YES: " + x)
print("\n--- Unimplemented? ---")
for x in unimplemented:
    print("NO : " + x)
