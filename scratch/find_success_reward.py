with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "function applycombatsuccessreward" in line.lower():
        out.append(f"L{idx+1}: {line.strip()}")
        # print next 50 lines
        for i in range(idx+1, min(idx+60, len(lines))):
            out.append(f"  {lines[i].rstrip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_success_reward.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
