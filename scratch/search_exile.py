with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'exileCard' in line:
            print(f"{idx+1}: {line.strip()}")
