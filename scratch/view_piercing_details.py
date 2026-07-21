with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- Lines 2980-3000 ---")
for i in range(2979, 3000):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

print("\n--- Lines 3740-3760 ---")
for i in range(3739, 3760):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
