import json
with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

with open('scratch/clean_names.txt', 'w', encoding='utf-8') as out:
    out.write("Listing all counter/spell-protection related cards:\n")
    for c in cards:
        id_val = c.get('id', '')
        name_val = c.get('name', '')
        if any(k in name_val for k in ['魔法反制', '法術保護', '終極無效化', '法術解析', '魔法炸彈客']) or 'NMG-0019' in id_val:
            out.write(f"ID: {id_val:<25} | Name: {name_val}\n")
