import json
import codecs

with codecs.open('data/decks.json', 'r', encoding='utf-8') as f:
    decks = json.load(f)

changed = False
for deck_name, cards in decks.items():
    new_cards = []
    for cid in cards:
        clean_cid = cid.strip()
        # Some invisible characters might not be stripped by just .strip()
        # Let's remove any non-ascii characters or weird spaces from the end
        clean_cid = clean_cid.replace('\u200b', '').replace('\u3000', '')
        # Remove trailing strange spaces
        import string
        clean_cid = ''.join(c for c in clean_cid if c in string.printable).strip()
        
        if clean_cid != cid:
            changed = True
        new_cards.append(clean_cid)
    decks[deck_name] = new_cards

if changed:
    with codecs.open('data/decks.json', 'w', encoding='utf-8') as f:
        json.dump(decks, f, ensure_ascii=False, indent=2)
    print("Fixed trailing whitespace in deck card IDs.")
else:
    print("No trailing whitespace found.")
