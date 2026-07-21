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
    backup_cards = json.load(f)

# Find missing cards in backup
with open('c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/cards.json', 'r', encoding='utf-8') as f:
    current_cards = json.load(f)

current_ids = {c.get("id") for c in current_cards}
missing = [c for c in backup_cards if str(c.get("id")).startswith("ART-") and c.get("id") not in current_ids]

print(f"Total missing: {len(missing)}")
if missing:
    print("Example 1:", missing[0])
    if len(missing) > 1:
        print("Example 2:", missing[1])
