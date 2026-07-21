import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx in range(8278, min(8292, len(lines))):
    output.append(f"Line {idx+1}: {lines[idx]}")

out_path = os.path.join(base_dir, "scratch/game_js_8283.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.writelines(output)

print("Saved to scratch/game_js_8283.txt")
