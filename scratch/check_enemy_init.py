def check_file(filepath):
    print(f"=== Checking {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    import re
    # Find xlwInitEnemyDeck definition
    match = re.search(r'function xlwInitEnemyDeck\(\).*?\{.*?\}', text, re.DOTALL)
    if match:
        print(match.group(0))
    else:
        print("xlwInitEnemyDeck not found")

check_file('static/game.js')
check_file('static/game_v8.js')
