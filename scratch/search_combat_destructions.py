import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "destroyUnit(" in line and idx > 4920 and idx < 5200:
        print(f"Line {idx+1}: {line.strip()}")
        # print context
        for j in range(idx-3, idx+5):
            print(f"  {j+1}: {lines[j]}")
