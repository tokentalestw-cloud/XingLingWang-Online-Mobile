import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

found = False
for idx, line in enumerate(lines):
    if "async function runEnemyTurn()" in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print the next 150 lines to see flow
        for j in range(idx, min(len(lines), idx+150)):
            print(f"  {j+1}: {lines[j]}")
        break
