import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if ('onclick' in line or 'click' in line) and ('field' in line or 'slot' in line or 'Card' in line):
        print(f"Line {idx+1}: {line.strip()}")
