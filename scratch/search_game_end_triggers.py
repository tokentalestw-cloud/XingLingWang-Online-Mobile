import os
import sys
import re

# Set encoding to utf-8 for stdout to prevent UnicodeEncodeErrors
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

def search_game_end_paths(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # We want to find any assignment to isGameOverFlag, e.g., isGameOverFlag = true
    # or execution of executeGameOverCalculations
    # or show result panel
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        line_lower = line.lower()
        if "isgameoverflag" in line_lower and "true" in line_lower:
            print(f"L{idx+1}: {line.strip()}")
            # Print 5 lines above and below
            for i in range(max(0, idx-5), min(len(lines), idx+6)):
                print(f"  {i+1}: {lines[i].rstrip()}")
            print("-" * 50)
            
        if "executegameovercalculations" in line_lower:
            if "function" not in line_lower:
                print(f"L{idx+1}: {line.strip()}")
                # Print 5 lines above and below
                for i in range(max(0, idx-5), min(len(lines), idx+6)):
                    print(f"  {i+1}: {lines[i].rstrip()}")
                print("-" * 50)

search_game_end_paths("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
search_game_end_paths("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
