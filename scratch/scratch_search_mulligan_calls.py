import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if "confirmMulligan" in line or "checkMulliganCompletion" in line:
        print(f"Line {idx}: {line.strip()}")
