import re

def search_exile_logic(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # search for XLW_exileExcessHandActive
    matches = [m.start() for m in re.finditer("XLW_exileExcessHandActive", content)]
    print(f"Found {len(matches)} occurrences of XLW_exileExcessHandActive")
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        if "XLW_exileExcessHandActive" in line:
            print(f"  L{idx+1}: {line.strip()}")

search_exile_logic("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
search_exile_logic("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
