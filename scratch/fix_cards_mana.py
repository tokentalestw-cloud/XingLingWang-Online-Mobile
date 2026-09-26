import json
import codecs

with codecs.open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

changed = False
for c in cards:
    if c.get('id') == 'R-NMG-0020-2':
        if c.get('mana') != 3:
            c['mana'] = 3
            changed = True
    elif c.get('id') == 'SR-NMG-0026':
        if c.get('mana') != 4:
            c['mana'] = 4
            changed = True

if changed:
    with codecs.open('data/cards.json', 'w', encoding='utf-8') as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)
    print("Fixed mana for R-NMG-0020-2 (set to 3) and SR-NMG-0026 (set to 4).")
else:
    print("Mana values are already correct.")
