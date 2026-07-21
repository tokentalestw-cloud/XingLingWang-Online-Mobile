import re

def search_game_over(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if "gameover" in line_lower or "game_over" in line_lower or "isgameover" in line_lower or "endgame" in line_lower or "settle" in line_lower:
            print(f"L{idx+1}: {line.strip()}")

print("Searching game.js:")
search_game_over("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nSearching game_v8.js:")
search_game_over("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
