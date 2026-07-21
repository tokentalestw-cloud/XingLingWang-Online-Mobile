import re
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

def find_literal_10(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        # Find "10" as a whole word or number, ignoring things like style widths, opacity, font size, etc.
        # e.g., turn 10, turn === 10, or just 10
        if "10" in line:
            # Let's filter out common UI styling things to focus on game logic
            if any(term in line_lower for term in ["width:", "height:", "opacity:", "font-size:", "100%", "border-radius:", "10px", "z-index:", "padding:", "1000", "font-weight:", "margin:", "top:", "left:", "right:", "bottom:", "box-shadow:"]):
                continue
            # Also filter out base64, long arrays, image paths, etc.
            if len(line) > 200:
                continue
            print(f"L{idx+1}: {line.strip()}")

print("Searching game.js:")
find_literal_10("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
print("\nSearching game_v8.js:")
find_literal_10("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
