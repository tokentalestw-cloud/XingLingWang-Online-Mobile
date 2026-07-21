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

with open('c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/cards.json', 'r', encoding='utf-8') as f:
    current_cards = json.load(f)

backup_art = [c for c in backup_cards if str(c.get("id")).startswith("ART-")]
current_art = [c for c in current_cards if str(c.get("id")).startswith("ART-")]

print(f"Total ART cards in backup: {len(backup_art)}")
print(f"Total ART cards in current: {len(current_art)}")

# See which ones in backup are not in current
current_ids = {c.get("id") for c in current_art}
missing_in_current = [c for c in backup_art if c.get("id") not in current_ids]

print(f"\nMissing in current but present in backup ({len(missing_in_current)}):")
for c in missing_in_current:
    print(f"  ID: {c.get('id')}, Name: {c.get('name')}, File: {c.get('original_file')}")
