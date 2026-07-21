import os
import sys

# Reconfigure stdout to use UTF-8
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

def get_context(filepath, start_line, end_line):
    lines_dict = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if start_line <= idx <= end_line:
                lines_dict[idx] = line
    return lines_dict

# Let's search and write context around matches to a file
out_path = os.path.join(base_dir, "scratch/prajna_context.txt")
with open(out_path, "w", encoding="utf-8") as out_f:
    for f_name in ["static/game.js", "static/game_v8.js"]:
        f_path = os.path.join(base_dir, f_name)
        if not os.path.exists(f_path):
            continue
        out_f.write(f"\n=================== {f_name} ===================\n")
        
        # Let's read lines and find lines with Prajna
        prajna_lines = []
        with open(f_path, "r", encoding="utf-8") as f:
            for idx, line in enumerate(f, 1):
                if any(term in line for term in ["般若", "Prajna", "hannya", "Hannya"]):
                    prajna_lines.append(idx)
        
        # Merge overlapping ranges
        ranges = []
        for line in prajna_lines:
            start = max(1, line - 15)
            end = line + 15
            if not ranges:
                ranges.append([start, end])
            else:
                last = ranges[-1]
                if start <= last[1]:
                    last[1] = max(last[1], end)
                else:
                    ranges.append([start, end])
        
        for r in ranges:
            out_f.write(f"\n--- Lines {r[0]} to {r[1]} ---\n")
            ctx = get_context(f_path, r[0], r[1])
            for l_no in sorted(ctx.keys()):
                out_f.write(f"{l_no}: {ctx[l_no]}")

print("Done. Context written to scratch/prajna_context.txt")
