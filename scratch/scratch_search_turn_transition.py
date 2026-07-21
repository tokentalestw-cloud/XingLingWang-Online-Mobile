import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("=== End Turn & Turn Start / Draw Logic ===")
for idx, line in enumerate(lines, 1):
    if "endTurn()" in line or "function endTurn" in line or "startTurn" in line or "data.action === \"end_turn\"" in line:
        print(f"Line {idx}: {line.strip()[:150]}")
        # print around
        for j in range(max(0, idx - 5), min(idx + 15, len(lines))):
            print(f"  {j+1}: {lines[j].strip()[:150]}")
        print("-" * 40)
