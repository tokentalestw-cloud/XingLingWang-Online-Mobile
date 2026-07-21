with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    js_content = f.read()

import re

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\mechanics_report.txt", "w", encoding="utf-8") as out:
    # Find occurrences of magic immune/resistance terms
    out.write("--- Magic Immune / Resistance ---\n")
    for idx, line in enumerate(js_content.splitlines()):
        if "magicImmune" in line or "魔抗" in line or "抗性" in line:
            if len(line.strip()) < 150:
                out.write(f"Line {idx+1}: {line.strip()}\n")

    # Find occurrences of indestructible/destruction immune terms
    out.write("\n--- Indestructible / Destruction Immune ---\n")
    for idx, line in enumerate(js_content.splitlines()):
        if "indestructible" in line or "破壞抗性" in line or "免疫破壞" in line or "indestruct" in line:
            if len(line.strip()) < 150:
                out.write(f"Line {idx+1}: {line.strip()}\n")
                
    # Find occurrences of "立即" (immediate effect) triggers
    out.write("\n--- Immediate Triggers ---\n")
    for idx, line in enumerate(js_content.splitlines()):
        if "立即" in line or "Immediate" in line or "summon" in line:
            if "function" in line or "if" in line or "case" in line or "id" in line:
                if len(line.strip()) < 150:
                    out.write(f"Line {idx+1}: {line.strip()}\n")
