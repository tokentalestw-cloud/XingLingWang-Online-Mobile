import json

with open("data/cards.json", "r", encoding="utf-8") as f:
    cards = json.load(f)

def belongsToDeck(c, deckName):
    if not c:
        return False
    idUpper = str(c.get("id") or "").upper()
    
    if deckName == "美術品":
        if "CAT" in idUpper or "VLG" in idUpper or "ORC" in idUpper:
            return False
    elif deckName == "喵喵賊":
        if "VLG" in idUpper or "ART" in idUpper or "ORC" in idUpper:
            return False
    elif deckName == "妖怪村莊":
        if "CAT" in idUpper or "ART" in idUpper or "ORC" in idUpper:
            return False
    elif deckName == "獸人":
        if "CAT" in idUpper or "VLG" in idUpper or "ART" in idUpper:
            return False

    if c.get("faction") == "中立" or c.get("race") == "中立" or idUpper.startswith("NEU-") or c.get("deck") == "中立":
        return True

    if deckName == "美術品":
        return c.get("faction") == "美術" or c.get("race") == "美術" or idUpper.startswith("ART-")
    if deckName == "喵喵賊":
        return c.get("faction") == "喵喵" or c.get("race") == "喵喵" or idUpper.startswith("CAT-")
    if deckName == "妖怪村莊":
        return c.get("faction") == "妖怪" or c.get("race") == "妖怪" or idUpper.startswith("VLG-")
    if deckName == "獸人":
        return c.get("faction") == "獸人" or c.get("race") == "獸人" or idUpper.startswith("ORC-") or "0RC-" in idUpper

    return False

for faction in ["妖怪村莊", "喵喵賊", "美術品", "獸人"]:
    matched = [c for c in cards if belongsToDeck(c, faction) and c.get("deck_eligible") is False]
    print(f"Faction {faction}: Count={len(matched)}")
    for c in matched:
        print(f"  ID: {c.get('id')}, Name: {c.get('name').encode('ascii', errors='replace').decode('ascii')}")
