import re

def scan_file(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to find any occurrence of:
    # 1. turn >= 10 or turn > 10 or turn == 10 or turn === 10
    # 2. any constant definition like FINAL_TURN or max turns
    # Let's search for matches using regex.
    # Let's print any lines containing "10" or "turn" where they are close or compared.
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if "10" in line or "turn" in line_lower:
            # Let's filter for comparisons like >=, >, ==, ===, <=, <, or assignments
            if any(x in line for x in [">", "<", "=", "!"]):
                # Let's print to check
                print(f"L{idx+1}: {line.strip()}")

print("Scanning game.js:")
scan_file("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nScanning game_v8.js:")
scan_file("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
