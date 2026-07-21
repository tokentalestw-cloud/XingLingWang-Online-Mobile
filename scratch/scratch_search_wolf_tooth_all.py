import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

output = []
for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    output.append(f"\n=== Searching in {f_name} ===\n")
    with open(f_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines, 1):
        if "血戰幫狼牙棒" in line:
            output.append(f"Line {idx}: {line.strip()}\n")
            # print surrounding 5 lines
            for j in range(max(0, idx - 5), min(len(lines), idx + 8)):
                output.append(f"  {j+1}: {lines[j].rstrip()}\n")
            output.append("-" * 40 + "\n")

out_path = os.path.join(base_dir, "scratch/wolf_tooth_search_all.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/wolf_tooth_search_all.txt")
