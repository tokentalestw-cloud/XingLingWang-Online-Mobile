import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if ('onclick =' in line or 'onclick=' in line) and ('card' in line or 'unit' in line or 'El' in line) and idx > 5000:
        print(f"Line {idx+1}: {line.strip()}")
