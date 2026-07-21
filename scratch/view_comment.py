with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(3721, 3725):
    print(f"Line {i+1}: {repr(lines[i])}")
