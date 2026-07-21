import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if "extra_summon_resolved" in line:
        output.append(f"Line {idx}: {line.strip()}")
        # print around
        for j in range(max(0, idx - 5), min(idx + 35, len(lines))):
            output.append(f"  {j+1}: {lines[j].strip()}")
        break

out_path = os.path.join(base_dir, "scratch/game_js_ws_handlers.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(output))

print("Saved to scratch/game_js_ws_handlers.txt")
