import json
with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

print("Listing all counter/spell-protection related cards:")
for c in cards:
    id_val = c.get('id', '')
    name_val = c.get('name', '')
    desc_val = c.get('effect_text', '')
    if any(k in name_val for k in ['魔法反制', '法術保護', '終極無效化', '法術解析', '魔法炸彈客']) or 'NMG-0019' in id_val:
        print(f"ID: {id_val} | Name: {name_val}")
