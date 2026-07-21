import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "resolveUnitCombat" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print around it
        for j in range(max(0, idx-5), min(len(lines), idx+10)):
            print(f"  {j+1}: {lines[j]}")
