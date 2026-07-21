with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "hasPiercing" in line or "piercing" in line:
        if len(line.strip()) < 120:
            print(f"Line {idx+1}: {line.strip()}")
