def check_assignments(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if 'playerExtraDeck =' in line or 'enemyExtraDeck =' in line:
            print(f"Line {idx+1}:")
            for j in range(max(0, idx-2), min(len(lines), idx+3)):
                print(f"  {j+1}: {lines[j]}", end="")

check_assignments('static/game.js')
check_assignments('static/game_v8.js')
