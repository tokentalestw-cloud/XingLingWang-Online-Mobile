import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if ('菜刀' in line or 'R-ORC-0034' in line or '戰斧牛排' in line) and idx < 2000:
        print(f"Line {idx+1}: {line.strip()}")
