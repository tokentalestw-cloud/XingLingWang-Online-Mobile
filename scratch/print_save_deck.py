with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
for idx, line in enumerate(lines):
    if 'def save_deck' in line:
        start_idx = idx
        break

if start_idx is not None:
    print(f"Found def save_deck at line {start_idx + 1}")
    for j in range(start_idx, min(len(lines), start_idx + 100)):
        print(f"{j+1}: {lines[j]}", end="")
else:
    print("def save_deck not found")
