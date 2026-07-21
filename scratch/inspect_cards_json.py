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

print(f"Total cards: {len(cards)}")
# Print keys of the first card
if cards:
    print("Keys of first card:", list(cards[0].keys()))
    print("Example first card:", cards[0])

# Count card prefixes (e.g. ART-, VLG-, CAT-)
prefixes = {}
for c in cards:
    cid = str(c.get("id", ""))
    prefix = cid.split('-')[0] if '-' in cid else cid[:3]
    prefixes[prefix] = prefixes.get(prefix, 0) + 1

print("\nCard counts by prefix:")
for pref, count in prefixes.items():
    print(f"  {pref}: {count}")

# Print first few cards for ART- prefix
art_cards = [c for c in cards if str(c.get("id")).startswith("ART-")]
print(f"\nTotal ART- cards: {len(art_cards)}")
if art_cards:
    print("Example ART card:", art_cards[0])
