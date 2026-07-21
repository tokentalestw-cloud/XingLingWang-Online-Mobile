import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "function changeActionPhase" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print around it
        for j in range(idx, min(len(lines), idx+60)):
            print(f"  {j+1}: {lines[j]}")
        break
