import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
# Handler 1 context
output.append("=== Handler 1 (Around 5892) ===\n")
for idx in range(5885, min(5920, len(lines))):
    output.append(f"{idx+1}: {lines[idx]}")

# Handler 2 context
output.append("\n=== Handler 2 (Around 6105) ===\n")
for idx in range(6095, min(6135, len(lines))):
    output.append(f"{idx+1}: {lines[idx]}")

out_path = os.path.join(base_dir, "scratch/both_equip_handlers.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/both_equip_handlers.txt")
