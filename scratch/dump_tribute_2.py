with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1849, 2000):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
