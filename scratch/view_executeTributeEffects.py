with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\executeTributeEffects_segment.txt', 'w', encoding='utf-8') as f_out:
    for idx in range(1734, 1798):
        if idx < len(lines):
            f_out.write(f"{idx+1}: {lines[idx]}")

print("Done")
