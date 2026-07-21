with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "function runEnemyTurn" in line:
        print(f"runEnemyTurn: L{idx+1}")
    elif "function endPlayerTurnAndRunEnemy" in line:
        print(f"endPlayerTurnAndRunEnemy: L{idx+1}")
