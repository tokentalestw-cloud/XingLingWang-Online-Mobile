with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    content = f.read()

pos = content.find("ws.onmessage = async (event) => {")
if pos == -1:
    pos = content.find("ws.onmessage = (event) => {")
if pos == -1:
    pos = content.find("ws.onmessage = function")

if pos != -1:
    # Match curly braces to find function end
    brace_count = 0
    started = False
    end_pos = pos
    for i in range(pos, len(content)):
        if content[i] == '{':
            brace_count += 1
            started = True
        elif content[i] == '}':
            brace_count -= 1
        if started and brace_count == 0:
            end_pos = i + 1
            break
    
    with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_ws_onmessage.js", "w", encoding="utf-8") as out:
        out.write(content[pos:end_pos])
    print("Successfully wrote scratch_ws_onmessage.js. Length:", end_pos - pos)
else:
    print("ws.onmessage not found!")
