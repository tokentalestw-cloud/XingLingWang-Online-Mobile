import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output_lines = []
found = False
for idx, line in enumerate(lines, 1):
    if "endPlayerTurnAndRunEnemy" in line:
        found = True
        output_lines.append(f"Line {idx}: {line}")
        for j in range(idx - 1, min(idx + 180, len(lines))):
            output_lines.append(f"{j+1}: {lines[j]}")
        break

out_path = os.path.join(base_dir, "scratch/endPlayerTurnAndRunEnemy_code.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.writelines(output_lines)

print("Done. Saved to scratch/endPlayerTurnAndRunEnemy_code.txt")
