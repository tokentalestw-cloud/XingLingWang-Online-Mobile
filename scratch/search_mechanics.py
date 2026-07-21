with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    js_content = f.read()

import re

# Find occurrences of magic immune/resistance terms
print("--- Magic Immune / Resistance ---")
for line in js_content.splitlines():
    if "magicImmune" in line or "魔抗" in line or "抗性" in line:
        if len(line.strip()) < 120:
            print(line.strip())

# Find occurrences of indestructible/destruction immune terms
print("\n--- Indestructible / Destruction Immune ---")
for line in js_content.splitlines():
    if "indestructible" in line or "破壞抗性" in line or "免疫破壞" in line:
        if len(line.strip()) < 120:
            print(line.strip())
            
# Find occurrences of "立即" (immediate effect) triggers
print("\n--- Immediate Triggers ---")
immediate_lines = []
for idx, line in enumerate(js_content.splitlines()):
    if "立即" in line or "Immediate" in line:
        immediate_lines.append((idx+1, line.strip()))
for idx, line in immediate_lines[:15]:
    print(f"Line {idx}: {line}")
