import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'magicImmune' in line and ('false' in line or 'null' in line or 'delete' in line or 'clean' in line):
        print(f"Line {idx+1}: {line.strip()}")
