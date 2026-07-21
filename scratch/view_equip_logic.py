with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look at lines 4900 to 5110
with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\equip_logic.txt', 'w', encoding='utf-8') as f_out:
    for i in range(4900, 5110):
        if i < len(lines):
            f_out.write(f"{i+1}: {lines[i]}")

print("Done")
