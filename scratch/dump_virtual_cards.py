import json

with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

vir_cards = [c for c in cards if c.get('faction') == '虛擬世界' or c.get('race') == '虛擬世界' or (c.get('id') and 'VIR' in c['id'].upper())]

with open('scratch/virtual_cards.txt', 'w', encoding='utf-8') as out:
    for c in vir_cards:
        is_extra = c.get('is_extra_deck', False) or c.get('deck_eligible') == False
        out.write(f"{c['id']} | {c['name']} | {c.get('type')} | Mana:{c.get('mana')} | Extra:{is_extra}\n")

print(f"Done! Dumped {len(vir_cards)} Virtual cards.")
