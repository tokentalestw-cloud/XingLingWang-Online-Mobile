import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json", 'r', encoding='utf-8') as f:
    cards = json.load(f)

factions = {}
for card in cards:
    fac = card.get("faction") or card.get("deck") or "Unknown"
    factions[fac] = factions.get(fac, 0) + 1

for fac, count in sorted(factions.items()):
    # Convert fac to printable or hex if unicode encode error might happen
    try:
        print(f"{fac}: {count}")
    except Exception:
        print(f"{fac.encode('utf-8')}: {count}")
