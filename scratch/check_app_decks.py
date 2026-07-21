import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for '/api/decks' or '/api/decks/save'
lines = text.splitlines()
for idx, l in enumerate(lines):
    if '/api/decks' in l:
        print(f"--- Line {idx+1} ---")
        for j in range(max(0, idx-5), min(len(lines), idx+20)):
            print(f"{j+1}: {lines[j]}")
