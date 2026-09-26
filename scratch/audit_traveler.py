import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)
with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    game_js = f.read()

target_deck = decks.get('特殊旅人_特殊旅人 預組', [])

with codecs.open('scratch/audit_traveler.txt', 'w', encoding='utf-8') as out:
    for cid in target_deck:
        card = next((c for c in cards if c.get('id') == cid), None)
        if not card: continue
        
        out.write(f"\n======================================\n")
        out.write(f"[{cid}] {card.get('name')}\n")
        out.write(f"TEXT: {card.get('effect_text')}\n")
        
        id_clean = cid.replace('-2', '').replace(' ', '')
        name = card.get('name', '').replace(' ', '')
        
        lines = game_js.split('\n')
        for i, line in enumerate(lines):
            if id_clean in line or (name and len(name) > 2 and name in line):
                out.write(f"  [L{i+1}] {line.strip()}\n")
