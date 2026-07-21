with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\magic_immune_check.txt", "w", encoding="utf-8") as out:
    for idx, line in enumerate(lines):
        if "magicImmune" in line:
            out.write(f"Line {idx+1}: {line.strip()}\n")
            # print 3 lines before and after
            start = max(0, idx - 3)
            end = min(len(lines), idx + 4)
            for j in range(start, end):
                out.write(f"  {j+1}: {lines[j]}")
            out.write("\n")
