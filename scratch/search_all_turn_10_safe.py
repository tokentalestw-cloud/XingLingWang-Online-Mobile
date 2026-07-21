import re
import sys

# Set encoding to utf-8 for stdout to prevent UnicodeEncodeErrors
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

def scan_file(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        # Search for turn combined with 10 or similar in the line
        # or search for turn count checks or 10 turns limit
        if "10" in line_lower and "turn" in line_lower:
            print(f"L{idx+1}: {line.strip()}")
        # Check if turn is being compared with 10 specifically
        elif re.search(r'\bturn\s*[><=!]=\s*10\b', line_lower) or re.search(r'\b10\s*[><=!]=\s*turn\b', line_lower):
            print(f"L{idx+1} (regex): {line.strip()}")

print("Scanning game.js:")
scan_file("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nScanning game_v8.js:")
scan_file("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
