with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '長脖子' in line or '雪女' in line:
        print(f"Line {idx+1}: {line.strip()}")
