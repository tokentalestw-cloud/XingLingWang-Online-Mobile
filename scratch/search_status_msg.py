with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", "r", encoding="utf-8") as f:
    game_js = f.read()

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    game_v8_js = f.read()

for filepath, content in [("game.js", game_js), ("game_v8.js", game_v8_js)]:
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        if "不能進行戰術佈陣" in line or "最後回合" in line:
            # check if it is not style/comment
            if "status" in line.lower() or "logbattle" in line.lower() or "setstatus" in line.lower():
                print(f"{filepath} L{idx+1}: {line.strip()}")
