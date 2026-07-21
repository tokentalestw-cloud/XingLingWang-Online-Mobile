import json
import os

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

targets = ['R-ORC-0025', 'ORC-0018', 'ORC-0005', 'R-ORC-0031', 'ORC-0008']

found = {}
for card in cards:
    id_ = card.get('id')
    if id_ in targets or any(t in id_ for t in targets):
        found[id_] = card

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\found_cards.json', 'w', encoding='utf-8') as f:
    json.dump(found, f, indent=2, ensure_ascii=False)

print("Done")
