import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "太極雕像" in line or "守護的斷臂雕像" in line or "啟動" in line:
        print(f"Line {idx+1}: {line.strip()}")
