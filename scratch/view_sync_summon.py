with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\sync_summon_dump.txt", "w", encoding="utf-8") as out:
    for i in range(6669, 6750):
        if i < len(lines):
            out.write(f"{i+1}: {lines[i]}")
