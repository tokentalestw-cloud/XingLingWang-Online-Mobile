import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if ('turn = ' in line or 'turn++' in line or 'turn+1' in line or 'turn + 1' in line) and ('return' not in line):
        print(f"Line {idx+1}: {line.strip()}")
