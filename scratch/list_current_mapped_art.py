import json
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

with open('c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

art_cards = [c for c in cards if str(c.get("id")).startswith("ART-")]
print(f"Current ART cards: {len(art_cards)}")

for idx, c in enumerate(art_cards, 1):
    print(f"  {idx:02d}: ID: {c.get('id')}, Name: {c.get('name')}, File: {c.get('original_file')}")
