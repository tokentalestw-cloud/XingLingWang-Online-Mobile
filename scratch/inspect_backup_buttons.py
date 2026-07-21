with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/backup/game.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("backup/game.js L5520-5540:")
for i in range(5520, 5540):
    print(f"{i+1}: {lines[i].rstrip()}")
