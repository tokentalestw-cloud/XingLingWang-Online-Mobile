import json
import codecs

with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

for c in cards:
    cid = c.get('id')
    if '-' in cid:
        base_id = cid.rsplit('-', 1)[0]
        if cid.endswith('-2') or cid.endswith('-3'):
            base_card = next((bc for bc in cards if bc.get('id') == base_id), None)
            if base_card:
                if c.get('mana') != base_card.get('mana'):
                    print(f"{cid} has mana {c.get('mana')}, but {base_card.get('id')} has mana {base_card.get('mana')}")
