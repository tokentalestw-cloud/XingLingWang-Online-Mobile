import re

def search_turn_checks(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if "turn" in line_lower:
            # check for numbers in the line, or comparisons
            if any(op in line for op in [">=", "==", "===", ">", "count", "remaining"]):
                # exclude simple increments like turn++ or object properties like turn: turn
                if not ("turn++" in line or "turn:" in line or "next_turn" in line or "turn = data" in line or "turn = s" in line):
                    print(f"L{idx+1}: {line.strip()}")

print("Searching game.js:")
search_turn_checks("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nSearching game_v8.js:")
search_turn_checks("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
