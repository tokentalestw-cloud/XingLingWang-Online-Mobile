import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\decks.json", 'r', encoding='utf-8') as f:
    decks = json.load(f)

for deck_name, card_list in sorted(decks.items()):
    print(f"Deck: {deck_name} (Length: {len(card_list)})")
