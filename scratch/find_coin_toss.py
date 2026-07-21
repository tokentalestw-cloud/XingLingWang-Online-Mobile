with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "coin" in line.lower() or "toss" in line.lower():
        out.append(f"L{idx+1}: {line.strip()}")

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_coin_toss.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
