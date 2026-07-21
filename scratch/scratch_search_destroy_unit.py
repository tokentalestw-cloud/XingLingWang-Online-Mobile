import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
found = False
for idx, line in enumerate(lines, 1):
    if "async function destroyUnit(" in line:
        found = True
        output.append(f"Line {idx}: {line}")
        for j in range(idx - 1, min(idx + 100, len(lines))):
            output.append(f"{j+1}: {lines[j]}")
        break

if found:
    out_path = os.path.join(base_dir, "scratch/destroyUnit_code.txt")
    with open(out_path, "w", encoding="utf-8") as f_out:
        f_out.writelines(output)
    print("Saved to scratch/destroyUnit_code.txt")
else:
    print("destroyUnit not found")
