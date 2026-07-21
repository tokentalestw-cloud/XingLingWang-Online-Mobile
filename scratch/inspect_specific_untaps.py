import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in [2650, 6770]:
    print(f"\n--- Around Line {idx+1} ---")
    for i in range(idx - 10, idx + 15):
        if i < len(lines):
            print(f"  {i+1}: {lines[i].strip()}")
