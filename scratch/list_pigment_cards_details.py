# -*- coding: utf-8 -*-
import json

cards_path = r"data/cards.json"
out_path = r"C:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\pigment_details.txt"

with open(cards_path, 'r', encoding='utf-8') as f:
    cards = json.load(f)

pigment_ids = ["ART-0032", "R-ART-0022", "R-ART-0023", "R-ART-0024", "R-ART-0032", "R-ART-0033", "R-ART-0045", "R-ART-0046", "R-ART-0049", "SSR-ART-0049"]
selected = [c for c in cards if c['id'] in pigment_ids]

with open(out_path, 'w', encoding='utf-8') as f:
    for c in selected:
        f.write(json.dumps(c, ensure_ascii=False, indent=2) + "\n\n")

print("Wrote details of selected cards.")
