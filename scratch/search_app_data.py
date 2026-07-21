import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r"app.py"
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

for idx, line in enumerate(lines):
    if "cards.json" in line or "decks.json" in line:
        print(f"Line {idx+1}: {line.strip()}")
