import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

line_569 = lines[568]
print(f"Unicode points: {[ord(c) for c in line_569]}")
print(f"Characters: {line_569}")
