with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(2132, 2486):
    line = lines[i]
    if "else if" in line or "if (" in line:
        if "card." in line or "id" in line:
            print(f"Line {i+1}: {line.strip()}")
