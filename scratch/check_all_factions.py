import json
with open('data/cards.json', 'r', encoding='utf-8') as f:
    cards = json.load(f)

def normDeckName(v):
    v = v.strip()
    if '藝術' in v or '中立' in v: return '藝術品'
    if '妖怪' in v: return '妖怪村莊'
    if '喵' in v or '貓' in v: return '喵喵賊'
    if '獸' in v: return '獸人'
    return '喵喵賊'

def belongsToDeck(c, deckName):
    deckName = normDeckName(deckName)
    idUpper = c.get('id', '').upper()
    if deckName == '藝術品':
        if 'CAT' in idUpper or 'VLG' in idUpper or 'ORC' in idUpper:
            return False
    elif deckName == '喵喵賊':
        if 'VLG' in idUpper or 'ART' in idUpper or 'ORC' in idUpper:
            return False
    elif deckName == '妖怪村莊':
        if 'CAT' in idUpper or 'ART' in idUpper or 'ORC' in idUpper:
            return False
    elif deckName == '獸人':
        if 'CAT' in idUpper or 'VLG' in idUpper or 'ART' in idUpper:
            return False

    if c.get('faction') == '中立' or c.get('race') == '中立' or idUpper.startswith('NEU-') or c.get('deck') == '中立':
        return True

    if deckName == '藝術品':
        return c.get('faction') == '藝術品' or c.get('race') == '藝術品' or idUpper.startswith('ART-')
    if deckName == '喵喵賊':
        return c.get('faction') == '喵喵賊' or c.get('race') == '喵喵賊' or idUpper.startswith('CAT_') or idUpper.startswith('CAT-')
    if deckName == '妖怪村莊':
        return c.get('faction') == '妖怪村莊' or c.get('race') == '妖怪村莊' or idUpper.startswith('VLG_') or idUpper.startswith('VLG-')
    if deckName == '獸人':
        return c.get('faction') == '獸人' or c.get('race') == '獸人' or idUpper.startswith('ORC_') or idUpper.startswith('ORC-')
    return c.get('deck') == deckName or c.get('faction') == deckName or c.get('race') == deckName

for faction in ["藝術品", "妖怪村莊", "喵喵賊", "獸人"]:
    matched = [c for c in cards if belongsToDeck(c, faction) and c.get('deck_eligible') is False]
    print(f"{faction} matching extra cards ({len(matched)}):")
    for c in matched:
        print(f"  {c['id']}: {c['name']}")
