import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
found = False
for idx, line in enumerate(lines, 1):
    if "function playCard" in line or "function useCard" in line or "function castSpell" in line or "clickCard" in line:
        found = True
        print(f"Line {idx}: {line.strip()}")
        for j in range(idx - 10, min(len(lines), idx + 80)):
            output.append(f"{j+1}: {lines[j]}")
        break

if found:
    out_path = os.path.join(base_dir, "scratch/play_card_logic.txt")
    with open(out_path, "w", encoding="utf-8") as f_out:
        f_out.writelines(output)
    print("Saved to scratch/play_card_logic.txt")
else:
    print("playCard not found")
