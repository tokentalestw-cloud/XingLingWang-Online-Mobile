# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = json.load(open('data/cards.json', encoding='utf-8'))
    js_content = open('static/game_v8.js', encoding='utf-8').read()

    unmentioned = []
    for c in cards:
        cid = c.get('id')
        name = c.get('name')
        if not c.get('deck_eligible', True):
            continue
        is_unmentioned = (cid not in js_content) and (name not in js_content)
        if is_unmentioned:
            unmentioned.append(c)

    by_fac = {}
    for c in unmentioned:
        fac = c.get('faction') or c.get('deck') or 'Unknown'
        by_fac.setdefault(fac, []).append(c)

    out = open('scratch/all_unmentioned_cards.txt', 'w', encoding='utf-8')
    out.write(f"Total remaining unimplemented cards: {len(unmentioned)}\n\n")
    for fac, lst in sorted(by_fac.items()):
        out.write(f"=========================================\n")
        out.write(f"Faction: {fac} (Count: {len(lst)})\n")
        out.write(f"=========================================\n")
        for c in lst:
            out.write(f"ID: {c.get('id')} | Name: {c.get('name')} | Type: {c.get('type')}\n")
            out.write(f"Effect: {c.get('effect_text')}\n\n")
    out.close()
    print("Dumps written to scratch/all_unmentioned_cards.txt")

if __name__ == '__main__':
    main()
