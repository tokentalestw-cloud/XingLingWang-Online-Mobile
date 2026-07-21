import os
import json
import shutil
from pathlib import Path

# Paths
cards_file = Path("data/cards.json")
src_dir = Path("C:/Users/a2132/Downloads/星靈王圖片/虛擬世界")
dest_dir = Path("static/card_images")

# Load existing cards
if cards_file.exists():
    try:
        cards = json.loads(cards_file.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read cards.json: {e}")
        cards = []
else:
    cards = []

# Get all images in src_dir
if not src_dir.exists():
    print(f"Error: Source directory {src_dir} does not exist.")
    exit(1)

valid_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
images = sorted([f for f in os.listdir(src_dir) if f.endswith(valid_extensions)])

print(f"Found {len(images)} images in {src_dir}")

# Create dest_dir if not exists
dest_dir.mkdir(parents=True, exist_ok=True)

imported_count = 0
for idx, img_name in enumerate(images, 1):
    # VIR-001, VIR-002, etc. (using 3 digits for consistency with CAT-, VLG-, and ORC-)
    card_id = f"VIR-{idx:03d}"
    clean_id = card_id.lower().replace("-", "_")
    dest_filename = f"{clean_id}.jpeg"
    dest_path = dest_dir / dest_filename
    
    src_path = src_dir / img_name
    
    # Copy image
    try:
        shutil.copy2(src_path, dest_path)
    except Exception as e:
        print(f"Failed to copy {img_name}: {e}")
        continue
        
    # Check if card already exists in database
    existing_card = next((c for c in cards if c.get("id") == card_id), None)
    if existing_card:
        # Update it
        existing_card["original_file"] = f"虛擬世界/{img_name}"
        existing_card["image"] = f"/static/card_images/{dest_filename}"
    else:
        # Create new card with default template properties
        new_card = {
            "id": card_id,
            "name": f"虛擬世界卡牌 {idx:03d}",
            "deck": "虛擬世界",
            "type": "unit",
            "faction": "虛擬世界",
            "race": "虛擬世界",
            "attack": "0",
            "score": 0,
            "tribute": 0,
            "keywords": [],
            "effect_text": "",
            "image": f"/static/card_images/{dest_filename}",
            "original_file": f"虛擬世界/{img_name}",
            "deck_eligible": True,
            "mana": 0,
            "usable_phases": [],
            "trigger_condition": ""
        }
        cards.append(new_card)
    imported_count += 1

# Sort cards by ID
cards.sort(key=lambda x: x.get("id", ""))

# Save cards back to cards.json
try:
    cards_file.write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Successfully imported {imported_count} cards into cards.json!")
except Exception as e:
    print(f"Failed to write cards.json: {e}")
