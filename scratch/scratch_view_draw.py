import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if "function draw(" in line or "draw(n)" in line:
        print(f"Line {idx}: {line.strip()}")
        # print next 30 lines
        for j in range(idx, min(idx + 50, len(lines))):
            print(f"  {j+1}: {lines[j].strip()}")
        break
