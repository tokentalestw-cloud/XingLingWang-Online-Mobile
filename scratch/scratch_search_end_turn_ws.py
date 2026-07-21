import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for j in range(6160, min(6220, len(lines))):
    output.append(f"{j+1}: {lines[j]}")

out_path = os.path.join(base_dir, "scratch/end_turn_ws.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.writelines(output)

print("Saved to scratch/end_turn_ws.txt")
