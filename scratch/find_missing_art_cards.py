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

with open('c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/data/art_full_manifest.json', 'r', encoding='utf-8') as f:
    art_manifest = json.load(f)

current_art_ids = {c.get("id") for c in cards if str(c.get("id")).startswith("ART-")}
manifest_art_cards = art_manifest.get("cards", [])

print(f"Current artwork cards in cards.json: {len(current_art_ids)}")
print(f"Artwork cards in manifest: {len(manifest_art_cards)}")

missing = []
for mc in manifest_art_cards:
    mid = mc.get("id")
    if mid not in current_art_ids:
        missing.append(mc)

print(f"\nMissing artwork cards ({len(missing)}):")
for idx, mc in enumerate(missing, 1):
    print(f"  {idx:02d}: ID: {mc.get('id')}, Name: {mc.get('name')}, Image: {mc.get('image')}")
