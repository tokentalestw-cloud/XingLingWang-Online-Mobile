import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json", 'r', encoding='utf-8') as f:
    cards = json.load(f)

factions = {}
for card in cards:
    fac = card.get("faction") or card.get("deck") or "Unknown"
    if fac not in factions:
        factions[fac] = []
    factions[fac].append(card)

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\factions_report.txt", "w", encoding="utf-8") as f:
    for fac, list_cards in sorted(factions.items()):
        f.write(f"Faction: {fac} (Count: {len(list_cards)})\n")
        # Write first 5 card names and IDs
        for c in list_cards[:10]:
            f.write(f"  - {c.get('id')}: {c.get('name')} ({c.get('type')})\n")
        f.write("\n")
