with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

targets = ['R-ORC-0025', 'ORC-0018', 'ORC-0005', 'R-ORC-0031', 'ORC-0008']

with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\orc_implementations.txt", "w", encoding="utf-8") as out:
    for target in targets:
        out.write(f"=== Target: {target} ===\n")
        found = False
        for idx, line in enumerate(lines):
            if target in line:
                found = True
                out.write(f"Line {idx+1}: {line.strip()}\n")
                # Print 5 lines before and after
                start = max(0, idx - 5)
                end = min(len(lines), idx + 6)
                for j in range(start, end):
                    out.write(f"  {j+1}: {lines[j]}")
                out.write("\n")
        if not found:
            out.write("NOT FOUND\n\n")
