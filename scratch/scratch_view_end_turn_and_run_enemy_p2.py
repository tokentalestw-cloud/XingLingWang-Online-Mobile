import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output_lines = []
for j in range(3900, min(4150, len(lines))):
    output_lines.append(f"{j+1}: {lines[j]}")

out_path = os.path.join(base_dir, "scratch/endPlayerTurnAndRunEnemy_code_p2.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.writelines(output_lines)

print("Done. Saved to scratch/endPlayerTurnAndRunEnemy_code_p2.txt")
