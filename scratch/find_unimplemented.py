import json

# Load cards from cards.json
with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json", 'r', encoding='utf-8') as f:
    cards = json.load(f)

# Load game_v8.js content
with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    js_content = f.read()

# Filter out non-deck eligible cards or check all cards
unmentioned = []
for c in cards:
    cid = c.get("id")
    name = c.get("name")
    if not c.get("deck_eligible", True):
        continue
    # If the card id or card name is not mentioned in game_v8.js (case-insensitive check)
    if cid not in js_content and name not in js_content:
        unmentioned.append(c)

# Save unmentioned cards report
with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\unmentioned_cards.txt", "w", encoding="utf-8") as f:
    f.write(f"Total unmentioned eligible cards: {len(unmentioned)}\n\n")
    # Group by faction
    by_fac = {}
    for c in unmentioned:
        fac = c.get("faction") or c.get("deck") or "Unknown"
        by_fac[fac] = by_fac.get(fac, []) + [c]
    
    for fac, list_cards in sorted(by_fac.items()):
        f.write(f"Faction: {fac} (Count: {len(list_cards)})\n")
        for c in list_cards:
            f.write(f"  - {c.get('id')}: {c.get('name')} (Type: {c.get('type')})\n")
            f.write(f"    Effect: {c.get('effect_text')}\n")
        f.write("\n")
