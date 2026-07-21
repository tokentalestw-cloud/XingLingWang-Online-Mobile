with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if '般若' in line or '智慧' in line or '憤怒' in line:
        print(f"Line {idx+1}: {line.strip()}")
