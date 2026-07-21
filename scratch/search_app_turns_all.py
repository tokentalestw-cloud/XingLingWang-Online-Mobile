import os
import sys

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("Scanning app.py for turn or game state:")
for idx, line in enumerate(lines):
    line_lower = line.lower()
    if "turn" in line_lower or "over" in line_lower or "limit" in line_lower or "end" in line_lower or "win" in line_lower or "10" in line_lower:
        print(f"L{idx+1}: {line.strip()}")
