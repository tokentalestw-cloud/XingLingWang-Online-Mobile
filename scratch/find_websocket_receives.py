import re

def extract_onmessage(filepath, output_list):
    output_list.append(f"=== ONMESSAGE IN {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Locate ws.onmessage or socket.onmessage
    pos = content.find("ws.onmessage")
    if pos == -1:
        pos = content.find("socket.onmessage")
    if pos == -1:
        output_list.append("No onmessage found!")
        return

    # Let's extract the block of code starting from pos, e.g. next 2000 lines or until end of function
    # Let's search for case "action" or message action routing
    lines = content[pos:pos+60000].split('\n')
    # Let's just output the lines that handle actions
    in_switch = False
    brace_depth = 0
    switch_lines = []
    
    for l in lines:
        if "switch" in l and ("action" in l or "data.action" in l or "msg.action" in l or "type" in l):
            in_switch = True
        if in_switch:
            switch_lines.append(l)
            brace_depth += l.count('{') - l.count('}')
            if brace_depth <= 0 and len(switch_lines) > 10:
                # We might have exited the switch block
                # but to be safe, let's collect a decent chunk of code
                if brace_depth < 0:
                    break
    
    output_list.extend(switch_lines)
    output_list.append("\n" + "="*80 + "\n")

out_lines = []
extract_onmessage("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", out_lines)
extract_onmessage("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", out_lines)

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_onmessage_handlers.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Done writing scratch_onmessage_handlers.txt")
