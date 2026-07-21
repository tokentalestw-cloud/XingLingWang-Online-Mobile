with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(4119, 4500):
    if idx < len(lines):
        line = lines[idx]
        if "field[" in line or "summon" in line or "tapped" in line:
            if "=" in line or "function" in line or "if" in line:
                print(f"Line {idx+1}: {line.strip()}")
