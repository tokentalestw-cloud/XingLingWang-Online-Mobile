def check_pushes(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if 'playerExtraDeck.push' in line or 'enemyExtraDeck.push' in line:
            print(f"Line {idx+1}: {line.strip()}")

check_pushes('static/game.js')
check_pushes('static/game_v8.js')
