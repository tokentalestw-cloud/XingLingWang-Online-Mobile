import json

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\data\decks.json", 'r', encoding='utf-8') as f:
    decks = json.load(f)

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\decks_utf8.txt", 'w', encoding='utf-8') as f:
    for deck_name, card_list in sorted(decks.items()):
        f.write(f"Deck: {deck_name} (Length: {len(card_list)})\n")
