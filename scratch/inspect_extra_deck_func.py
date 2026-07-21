import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function ' in line and ('ExtraDeck' in line or 'showExtra' in line or 'show_extra' in line):
        print(f"Line {idx+1}: {line.strip()}")
