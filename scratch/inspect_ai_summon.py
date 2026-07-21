import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'enemy' in line.lower() and ('summon' in line.lower() or 'field[' in line.lower()) and 'ai' in line.lower() and idx > 3000:
        print(f"Line {idx+1}: {line.strip()}")
