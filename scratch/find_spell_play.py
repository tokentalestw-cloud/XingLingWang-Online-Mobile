import re

def search_spell_play(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    print(f"=== SEARCHING {filepath} ===")
    results = []
    # Keywords to search for
    keywords = ["useMagicCard", "playSpell", "equip_spell", "goat_spell", "target", "spellChain", "ws.send", "resolved"]
    for idx, line in enumerate(lines):
        line_num = idx + 1
        # If we see things like target choosing, equip spells, goat spell, or ws.send(JSON.stringify({ action: "equip
        if any(kw in line for kw in ["equip_spell_resolved", "goat_spell_resolved", "temp_equip_spell_resolved"]):
            results.append((line_num, line.strip()))
        elif "goatSpellCard" in line or "XLW_equipSpellCard" in line or "XLW_tempEquipSpellCard" in line:
            results.append((line_num, line.strip()))
            
    with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_spell_play_details.txt", "w", encoding="utf-8") as f:
        for r in results:
            f.write(f"Line {r[0]}: {r[1]}\n")
            
search_spell_play("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
print("Done")
