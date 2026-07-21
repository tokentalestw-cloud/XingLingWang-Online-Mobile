with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for idx, line in enumerate(lines):
    if 'piercing' in line or '貫穿' in line or '菜刀' in line:
        output_lines.append(f"{idx+1}: {line.strip()}")

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\piercing_matches.txt', 'w', encoding='utf-8') as f_out:
    f_out.write('\n'.join(output_lines))

print("Done")
