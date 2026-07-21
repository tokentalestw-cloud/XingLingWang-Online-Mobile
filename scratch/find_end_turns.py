import re

def find_end_turns(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        if "end_turn" in line:
            surrounding = lines[max(0, idx-5):min(len(lines), idx+6)]
            if any("ws.send" in l for l in surrounding):
                print(f"L{idx+1}: {line.strip()}")
                # print surrounding lines
                for i in range(max(0, idx-4), min(len(lines), idx+7)):
                    print(f"  {i+1}: {lines[i].rstrip()}")
                print("-" * 50)

find_end_turns("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
find_end_turns("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
