with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "replace" in line and ("player" in line or "enemy" in line or "zone" in line):
        out.append(f"game_v8.js L{idx+1}: {line.strip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    lines_g = f.readlines()

for idx, line in enumerate(lines_g):
    if "replace" in line and ("player" in line or "enemy" in line or "zone" in line):
        out.append(f"game.js L{idx+1}: {line.strip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_zone_replacements.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
