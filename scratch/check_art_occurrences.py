with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\art_occurrences.txt", "w", encoding="utf-8") as out:
    for idx, line in enumerate(lines):
        if "藝術品" in line:
            out.write(f"Line {idx+1}: {line.strip()}\n")
