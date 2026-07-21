import zipfile
import json
import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

zip_path = 'C:/Users/a2132/Downloads/星靈王_v6_藝術品完整修正版_FINAL.zip'
if not os.path.exists(zip_path):
    print("Zip not found")
    sys.exit(0)

print("Extracting data/cards.json from zip...")
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        # read the cards.json content directly without extracting to file
        cards_content = z.read("data/cards.json")
        cards = json.loads(cards_content.decode('utf-8'))
        
    print(f"Total cards in zip's cards.json: {len(cards)}")
    art_cards = [c for c in cards if str(c.get("id")).startswith("ART-")]
    print(f"Total ART cards in zip's cards.json: {len(art_cards)}")
    
    # Check mapping
    mapped = 0
    unmapped = 0
    for idx, c in enumerate(art_cards, 1):
        orig = c.get("original_file")
        if orig:
            mapped += 1
            if idx <= 10 or idx > 50:
                print(f"  {idx:02d}: ID: {c.get('id')}, Name: {c.get('name')}, File: {orig}")
        else:
            unmapped += 1
            print(f"  {idx:02d}: ID: {c.get('id')}, Name: {c.get('name')} -> UNMAPPED!")
            
    print(f"\nSummary:\n  Mapped: {mapped}\n  Unmapped: {unmapped}")
except Exception as e:
    print("Error:", e)
