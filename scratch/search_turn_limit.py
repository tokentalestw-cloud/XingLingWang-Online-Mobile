import re

def search_turn_limit(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        # Look for numbers like 10, or variables related to turn limit / game over
        # e.g., turn >= 10, turn === 10, FINAL_TURN, etc.
        if "10" in line or "turn" in line.lower() or "limit" in line.lower():
            # Let's filter specifically for things checking turn number or 10
            # e.g. turn >=, turn >, turn ==, turn ===, or FINAL_TURN, or 10
            match = False
            line_lower = line.lower()
            if "turn" in line_lower and ("10" in line_lower or "final" in line_lower or "limit" in line_lower or "over" in line_lower):
                match = True
            if match:
                print(f"L{idx+1}: {line.strip()}")

print("Searching game.js:")
search_turn_limit("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nSearching game_v8.js:")
search_turn_limit("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
