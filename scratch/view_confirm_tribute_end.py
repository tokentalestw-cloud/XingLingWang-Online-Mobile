with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\confirm_tribute_end.txt', 'w', encoding='utf-8') as f_out:
    for idx in range(1780, 1835):
        if idx < len(lines):
            f_out.write(f"{idx+1}: {lines[idx]}")

print("Done")
