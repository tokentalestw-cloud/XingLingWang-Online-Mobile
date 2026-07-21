import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if "XLW_equipSpellCard" in line:
        output.append(f"Line {idx}: {line.strip()}")
        for j in range(max(0, idx - 10), min(len(lines), idx + 20)):
            output.append(f"  {j+1}: {lines[j].rstrip()}")
        output.append("-" * 50 + "\n")

out_path = os.path.join(base_dir, "scratch/equip_card_var_context.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/equip_card_var_context.txt")
