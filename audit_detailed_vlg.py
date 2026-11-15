import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

vlg_cards = [c for c in cards if c.get('faction') == '妖怪村莊' or c.get('deck') == '妖怪村莊' or 'VLG' in c.get('id', '')]

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    js_text = f.read()

# Let's inspect unique base card names (since cards have R, SR, SSR, SSSR, etc. variants)
# Group cards by base name / base id
groups = {}
for c in vlg_cards:
    cid = c['id']
    name = c['name']
    base_name = name.split(' ')[0].split('(')[0].strip()
    if base_name not in groups:
        groups[base_name] = []
    groups[base_name].append(c)

print(f"Total unique card base names in 妖怪村莊: {len(groups)}")

report = []

for base_name, card_list in groups.items():
    primary_card = card_list[0]
    effect = primary_card.get('effect_text', '').strip()
    cids = [c['id'] for c in card_list]
    
    # search where in js_text any cid or base_name appears
    matches = []
    for line_idx, line in enumerate(js_text.splitlines(), 1):
        if any(cid in line for cid in cids) or (len(base_name) >= 2 and base_name in line):
            matches.append((line_idx, line.strip()))
            
    report.append({
        'base_name': base_name,
        'cids': cids,
        'type': primary_card.get('type'),
        'effect': effect,
        'matches_count': len(matches),
        'matches': matches[:5]
    })

with open('vlg_base_report.txt', 'w', encoding='utf-8') as out:
    for r in report:
        out.write(f"=== {r['base_name']} ({', '.join(r['cids'])}) [{r['type']}] ===\n")
        out.write(f"Effect: {r['effect']}\n")
        out.write(f"Matches ({r['matches_count']}):\n")
        for idx, l in r['matches']:
            out.write(f"  L{idx}: {l}\n")
        out.write("\n")

print("Generated vlg_base_report.txt")
