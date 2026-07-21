import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json", 'r', encoding='utf-8') as f:
    cards = json.load(f)

for c in cards:
    if "負能量" in c.get("name") or "負能量" in c.get("effect_text"):
        print(f"ID: {c.get('id')}, Name: {c.get('name')}, Type: {c.get('type')}, Effect: {c.get('effect_text')}")
