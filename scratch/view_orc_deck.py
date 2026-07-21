import json

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)

# Find "獸人" deck
orc_deck = decks.get("獸人", [])
print("Orc deck cards count:", len(orc_deck))
print("Cards:", orc_deck)
