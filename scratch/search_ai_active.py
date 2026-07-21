import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "sculptureEffectUsedTurn" in line or "Taichi" in line or "taichi" in line:
        if idx > 9500: # past field_onclick
            print(f"Line {idx+1}: {line.strip()}")
