def find_sync_block(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    start_line = -1
    for idx, line in enumerate(lines):
        if 'data.action === "sync_game_state"' in line or 'data.action === \'sync_game_state\'' in line:
            start_line = idx + 1
            print(f"Start line: {start_line}")
            # print next 40 lines
            for i in range(idx, min(idx+45, len(lines))):
                print(f"  {i+1}: {lines[i].rstrip()}")
            break

find_sync_block("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
find_sync_block("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
