import re

def search_keywords(filepath, keywords, output_list):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    output_list.append(f"=== SEARCHING {filepath} ===")
    for idx, line in enumerate(lines):
        line_num = idx + 1
        for kw in keywords:
            if kw in line:
                output_list.append(f"L{line_num} ({kw}): {line.strip()}")
                break

out = []
search_keywords("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", [
    "spellChainStack",
    "resolveLocalSpellChain",
    "equip_spell_resolved",
    "goat_spell_resolved",
    "spellCard",
    "goatSpellCard"
], out)

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_search_spells.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
