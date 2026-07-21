import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json", 'r', encoding='utf-8') as f:
    cards = json.load(f)

art_magics = [c for c in cards if c.get("faction") == "藝術品" and c.get("type") == "magic"]
for c in art_magics:
    print(f"ID: {c.get('id')}, Name: {c.get('name')}, Subtype: {c.get('art_subtype')}, Effect: {c.get('effect_text')}")
