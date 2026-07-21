import sys
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
cards_file = BASE / "data" / "cards.json"
decks_file = BASE / "data" / "decks.json"
js_file = BASE / "static" / "game_v8.js"

cards = json.loads(cards_file.read_text(encoding="utf-8"))
card_map = {c.get("id"): c for c in cards}
decks = json.loads(decks_file.read_text(encoding="utf-8"))
js_content = js_file.read_text(encoding="utf-8")

output = []

for deck_name, cids in decks.items():
    unimplemented = []
    for cid in cids:
        card = card_map.get(cid)
        if not card:
            continue
        eff = card.get("effect_text", "").strip()
        if eff and eff != "無" and eff != "無。":
            id_clean = cid.replace("-", "_")
            in_js = (cid in js_content) or (id_clean in js_content) or (card.get("name") in js_content)
            if not in_js:
                unimplemented.append(card)
    output.append(f"Deck: {deck_name} | Total in deck: {len(cids)} | Unimplemented: {len(unimplemented)}")
    for c in unimplemented:
        output.append(f"  [{c.get('id')}] {c.get('name')} | Effect: {c.get('effect_text')}")

Path(BASE / "scratch" / "deck_unimplemented_summary.txt").write_text("\n".join(output), encoding="utf-8")
print("Written summary to scratch/deck_unimplemented_summary.txt")
