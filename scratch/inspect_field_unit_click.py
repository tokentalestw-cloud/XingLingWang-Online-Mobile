import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(8800, 8950):
    if i < len(lines):
        print(f"{i+1}: {lines[i].strip()}")
