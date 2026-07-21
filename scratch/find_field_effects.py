with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "恐怖的井" in line or "playerField" in line or "enemyField" in line:
        out.append(f"L{idx+1}: {line.strip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_field_effects.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
