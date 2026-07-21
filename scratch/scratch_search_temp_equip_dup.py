import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
occurrences = []
for idx, line in enumerate(lines, 1):
    if 'data.action === "temp_equip_spell_resolved"' in line:
        occurrences.append(idx)

print(f"Found {len(occurrences)} occurrences: {occurrences}")
for occ in occurrences:
    output.append(f"\n=== Occurrence at Line {occ} ===\n")
    for j in range(occ - 15, min(len(lines), occ + 25)):
        output.append(f"{j+1}: {lines[j]}")

out_path = os.path.join(base_dir, "scratch/temp_equip_duplicates.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/temp_equip_duplicates.txt")
