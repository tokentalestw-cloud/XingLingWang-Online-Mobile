with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'action:' in line and ('zone' in line or 'idx' in line):
        # print around the match
        start = max(0, idx - 2)
        end = min(len(lines), idx + 5)
        print(f"--- Line {idx+1} ---")
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].strip()}")
