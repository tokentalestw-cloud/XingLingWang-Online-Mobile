import sys
import difflib

# Safe print setup
if sys.stdout.encoding != 'utf-8':
    try:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    except Exception:
        pass

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/backup/game.js", "r", encoding="utf-8") as f:
    backup_lines = f.readlines()

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    current_lines = f.readlines()

def show_lines(lines, start_idx, num):
    for i in range(start_idx, min(len(lines), start_idx + num)):
        print(f"  {i+1}: {lines[i].rstrip()}")

# Let's find functions or variable names like "stableActionPanel" in current game.js
# and print them.
print("=== Current stableActionPanel lines ===")
for idx, line in enumerate(current_lines):
    if "stableActionPanel" in line:
        show_lines(current_lines, max(0, idx - 5), 15)
        print("-" * 50)
        break
