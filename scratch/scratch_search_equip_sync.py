import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if "equip_spell_resolved" in line or "temp_equip_spell_resolved" in line:
        output.append(f"Line {idx}: {line.strip()}")
        # print context
        for j in range(max(0, idx - 3), min(len(lines), idx + 25)):
            output.append(f"  {j+1}: {lines[j].rstrip()}")
        output.append("-" * 40)

out_path = os.path.join(base_dir, "scratch/equip_sync_code.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("\n".join(output))

print("Saved to scratch/equip_sync_code.txt")
