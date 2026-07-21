import json
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

with open('c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/backup_pre_cleanup/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

art_cards = [c for c in cards if str(c.get("id")).startswith("ART-")]
print(f"Total ART cards in backup: {len(art_cards)}")

mapped = 0
unmapped = 0
for c in art_cards:
    orig = c.get("original_file")
    if orig:
        mapped += 1
        print(f"  {c.get('id')} ({c.get('name')}): {orig}")
    else:
        unmapped += 1

print(f"\nSummary:\n  Mapped: {mapped}\n  Unmapped: {unmapped}")
