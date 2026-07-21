import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)

print("Decks available:")
for deck_name, cards in decks.items():
    print(f"Deck: {deck_name}, total cards: {len(cards)}")
