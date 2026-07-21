import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '抗性' in line or '免疫' in line or 'immune' in line or 'Immune' in line:
        print(f"Line {idx+1}: {line.strip()}")
