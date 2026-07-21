import json
with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open('scratch/artwork_subtypes.txt', 'w', encoding='utf-8') as out:
    for c in cards:
        faction = c.get('faction', '')
        deck = c.get('deck', '')
        id_val = c.get('id', '')
        if faction == '藝術品' or deck == '藝術品' or 'ART' in id_val:
            name = c.get('name', '')
            subtype = c.get('art_subtype', '')
            out.write(f"ID: {id_val:<15} | Name: {name:<20} | Subtype: {subtype}\n")
