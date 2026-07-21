with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/backup/game.js", "r", encoding="utf-8") as f:
    backup_lines = f.readlines()

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    current_lines = f.readlines()

# Let's search where window.XLW_FINAL_TURN was in backup, and print what is currently at that place
targets = [5528, 5531, 5749, 6274, 7075, 7085, 7577, 7589, 8121, 8136, 8762, 8777, 9318, 9333]
for t in targets:
    print(f"--- Backup L{t}: {backup_lines[t-1].strip()}")
    # Let's look for similar text in current_lines around that line
    start = max(0, t - 20)
    end = min(len(current_lines), t + 20)
    found = False
    for idx in range(start, end):
        # check if it contains a similar function or keyword
        # just print current lines in that window to see what is there
        pass
    print(f"Current L{t} range:")
    for idx in range(max(0, t-3), min(len(current_lines), t+4)):
        print(f"  {idx+1}: {current_lines[idx].rstrip()}")
