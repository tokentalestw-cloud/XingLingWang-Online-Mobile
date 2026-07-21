import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if "draw(" in line:
        output.append(f"Line {idx}: {line.strip()}")

out_path = os.path.join(base_dir, "scratch/draw_calls.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(output))

print(f"Done. Found {len(output)} draw calls.")
