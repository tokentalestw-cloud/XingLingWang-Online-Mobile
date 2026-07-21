with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = 0
for i in range(2485, 0, -1):
    line = lines[i]
    if "function" in line:
        print(f"Line {i+1}: {line.strip()}")
        found += 1
        if found >= 5:
            break
