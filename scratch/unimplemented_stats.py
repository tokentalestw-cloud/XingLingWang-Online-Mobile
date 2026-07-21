# -*- coding: utf-8 -*-
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    cards = json.load(open('data/cards.json', encoding='utf-8'))
    js_content = open('static/game_v8.js', encoding='utf-8').read()

    by_fac = {}
    total_unmentioned = 0
    for c in cards:
        cid = c.get('id')
        name = c.get('name')
        if not c.get('deck_eligible', True):
            continue
        is_unmentioned = (cid not in js_content) and (name not in js_content)
        fac = c.get('faction') or c.get('deck') or 'Unknown'
        by_fac.setdefault(fac, {'total': 0, 'unmentioned': 0})
        by_fac[fac]['total'] += 1
        if is_unmentioned:
            by_fac[fac]['unmentioned'] += 1
            total_unmentioned += 1

    print(f"Total cards in DB: {len(cards)}")
    print(f"Total eligible cards: {sum(x['total'] for x in by_fac.values())}")
    print(f"Total unmentioned/unimplemented: {total_unmentioned}")
    print("-" * 50)
    for fac, stats in sorted(by_fac.items()):
        print(f"{fac}: {stats['unmentioned']} / {stats['total']} unimplemented")

if __name__ == '__main__':
    main()
