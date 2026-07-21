with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
for idx, line in enumerate(lines):
    if "swap_units" in line.lower() or "swap" in line.lower():
        if "ws.send" in line or "socket.send" in line or "action" in line:
            out.append(f"L{idx+1}: {line.strip()}")
            # print surrounding lines
            for i in range(max(0, idx-2), min(idx+6, len(lines))):
                out.append(f"  {i+1}: {lines[i].rstrip()}")
            out.append("-" * 50)

with open("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/scratch/scratch_swap_units.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("Done")
