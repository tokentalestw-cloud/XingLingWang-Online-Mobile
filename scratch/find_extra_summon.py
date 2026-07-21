with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "extra_summon_resolved" in line:
        out.append(f"L{idx+1}: {line.strip()}")
        # print surrounding lines
        for i in range(max(0, idx-4), min(idx+6, len(lines))):
            out.append(f"  {i+1}: {lines[i].rstrip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_extra_summon.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
