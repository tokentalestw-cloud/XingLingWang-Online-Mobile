def find_lines_resolve(filepath):
    print(f"=== {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if "function resolveLocalSpellChain()" in line:
            # Let's count braces to find the end
            brace_count = 0
            started = False
            for i in range(idx, len(lines)):
                l = lines[i]
                if '{' in l:
                    brace_count += l.count('{')
                    started = True
                if '}' in l:
                    brace_count -= l.count('}')
                if started and brace_count == 0:
                    print(f"Start line: {idx+1}")
                    print(f"End line: {i+1}")
                    # print last 10 lines
                    for j in range(i-6, i+2):
                        print(f"  {j+1}: {lines[j].rstrip()}")
                    break
            break

find_lines_resolve("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game.js")
find_lines_resolve("c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed/static/game_v8.js")
