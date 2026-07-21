with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    content = f.read()

pos = content.find("ws.onmessage")
if pos != -1:
    print("Found ws.onmessage in game_v8.js:")
    print(content[pos:pos+2000])
else:
    print("ws.onmessage NOT found in game_v8.js")

pos_game = content.find("ws.onmessage")
