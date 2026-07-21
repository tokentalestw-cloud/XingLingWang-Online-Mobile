import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)

orc_cids = decks.get('獸人', [])
unique_orc_cids = list(set(orc_cids))

print("Orc cards with effects:")
count = 0
for cid in unique_orc_cids:
    card_obj = None
    for c in cards:
        if c.get('id') == cid:
            card_obj = c
            break
    if not card_obj:
        continue
    effect = card_obj.get('effect_text', '')
    if effect and effect.strip() != '':
        count += 1
        print(f"{count}. [{cid}] {card_obj.get('name')} ({card_obj.get('type')}, Cost: {card_obj.get('cost')}, Atk: {card_obj.get('attack')}, Stars: {card_obj.get('tribute')}): {effect}")
