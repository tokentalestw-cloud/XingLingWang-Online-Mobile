import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== Finding endTurn ===")
found = False
for idx, line in enumerate(lines, 1):
    if "function endTurn" in line or "async function endTurn" in line:
        found = True
        print(f"Line {idx}: {line.strip()}")
        for j in range(idx, min(idx + 100, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        break
if not found:
    print("endTurn function not found")
