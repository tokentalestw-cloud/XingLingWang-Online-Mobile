import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for i in range(7340, 7390):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}")
