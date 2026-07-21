import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
for idx, line in enumerate(lines, 1):
    if "ws.send" in line:
        block = "".join(lines[idx-1:idx+15])
        if "equip" in block or "spell" in block:
            output.append(f"Line {idx}:")
            output.append(block)
            output.append("-" * 50 + "\n")

out_path = os.path.join(base_dir, "scratch/ws_equip_sends.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/ws_equip_sends.txt")
