import re
import sys

# Ensure utf-8 is used for stdout if we print anything
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

def find_sends(filepath, output_list):
    output_list.append(f"=== SEARCHING {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # regex for ws.send(JSON.stringify({...})) or socket.send(JSON.stringify({...}))
    pattern = re.compile(r'(\w+)\.send\(\s*JSON\.stringify\(')
    matches = pattern.finditer(content)
    for m in matches:
        start_char = m.start()
        line_num = content[:start_char].count('\n') + 1
        
        # Extract surrounding context
        lines = content[start_char:start_char+500].split('\n')
        output_list.append(f"Line {line_num}:")
        for l in lines[:10]:
            output_list.append(f"  {l}")
        output_list.append("-" * 50)

out_lines = []
find_sends("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js", out_lines)
find_sends("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", out_lines)

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_websocket_sends.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("Done writing scratch_websocket_sends.txt")
