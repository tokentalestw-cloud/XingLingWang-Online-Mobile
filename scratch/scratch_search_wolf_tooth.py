import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"
game_js_path = os.path.join(base_dir, "static/game_v8.js")

with open(game_js_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

output = []
occurrences = []
for idx, line in enumerate(lines, 1):
    if '血戰幫狼牙棒' in line and 'window.XLW_equipSpellCard = card;' in lines[idx]:
        occurrences.append(idx)
    elif '血戰幫狼牙棒' in line and 'window.XLW_equipSpellCard = card;' in lines[idx+1]:
        occurrences.append(idx)
    elif '血戰幫狼牙棒' in line and 'window.XLW_equipSpellCard = card;' in lines[idx-1]:
        occurrences.append(idx)

# Let's search by string matches
occurrences = []
for idx, line in enumerate(lines, 1):
    if 'setStatus("【血戰幫狼牙棒】' in line or 'setStatus(\"【血戰幫狼牙棒】' in line:
        occurrences.append(idx)

print(f"Found {len(occurrences)} occurrences of setStatus for Wolf Tooth: {occurrences}")
for occ in occurrences:
    output.append(f"\n=== Occurrence at Line {occ} ===\n")
    for j in range(occ - 8, min(len(lines), occ + 12)):
        output.append(f"{j+1}: {lines[j]}")

out_path = os.path.join(base_dir, "scratch/wolf_tooth_duplicates.txt")
with open(out_path, "w", encoding="utf-8") as f_out:
    f_out.write("".join(output))

print("Saved to scratch/wolf_tooth_duplicates.txt")
