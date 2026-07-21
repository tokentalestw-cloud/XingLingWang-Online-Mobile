def find_lines(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if "function sendFullGameStateToOpponent" in line:
            print(f"Start line: {idx+1}")
            # print next 25 lines
            for i in range(idx, min(idx+25, len(lines))):
                print(f"  {i+1}: {lines[i].rstrip()}")
            break

find_lines("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
find_lines("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
