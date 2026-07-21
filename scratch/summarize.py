import json
from collections import defaultdict

with open('scratch_unimplemented_details.txt', encoding='utf-8') as f:
    match = json.load(f)

by_faction = defaultdict(list)
for c in match:
    fac = c.get('subdir') or c.get('faction') or 'Unknown'
    by_faction[fac].append(c)

with open('scratch_unimplemented_summary.txt', 'w', encoding='utf-8') as f_out:
    for fac, list_cards in sorted(by_faction.items()):
        f_out.write(f"Faction: {fac} ({len(list_cards)} cards)\n")
        for c in sorted(list_cards, key=lambda x: x['id']):
            f_out.write(f"  {c['id']}: {c['name']} | stars: {c.get('stars')} | type: {c.get('type')}\n")
            f_out.write(f"    Effect: {c.get('effect_description') or c.get('effect') or 'None'}\n\n")
print("Done summary")
