import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"static/game_v8.js"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "allCards" in line or "fetch(" in line:
        if any(keyword in line for keyword in ["=", "fetch", "load", "json"]):
            print(f"Line {idx+1}: {line.strip()}")
