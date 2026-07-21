with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'playerExtraDeck' in line or 'enemyExtraDeck' in line:
        # Filter out common rendering or check lines to find anything interesting
        if any(x in line for x in ['render', '.length', 'indexOf', 'splice', 'find', 'findIndex', '[]', 'const', 'let', 'showExtraDeckDetailModal']):
            continue
        print(f"Line {idx+1}: {line.strip()}")
