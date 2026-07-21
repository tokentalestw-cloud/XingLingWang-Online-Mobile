import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx in range(3080, 3450):
    if "else" in lines[idx] or "if (" in lines[idx]:
        print(f"{idx+1:4d} (ind {len(lines[idx]) - len(lines[idx].lstrip())}): {lines[idx]}")
