with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []
for idx, line in enumerate(lines):
    if 'playerUntap' in line or '召喚階段' in line or 'turn = ' in line:
        if len(line.strip()) < 100:
            output_lines.append(f"{idx+1}: {line.strip()}")

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\turn_start_matches.txt', 'w', encoding='utf-8') as f_out:
    f_out.write('\n'.join(output_lines))

print("Done")
