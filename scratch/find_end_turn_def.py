with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "function endPlayerTurnAndRunEnemy" in line:
        print(f"L{idx+1}: {line.strip()}")
        # print next 40 lines
        for i in range(idx+1, min(idx+45, len(lines))):
            print(f"  {i+1}: {lines[i].rstrip()}")
        break
