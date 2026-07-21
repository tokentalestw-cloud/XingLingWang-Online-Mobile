import sys

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

output_lines = []

for idx, line in enumerate(lines):
    if '.attached' in line or '.equip' in line or 'attachedCards' in line or 'equipped' in line:
        output_lines.append(f"Line {idx+1}: {line.strip()}")
        start = max(0, idx - 5)
        end = min(len(lines), idx + 8)
        for j in range(start, end):
            output_lines.append(f"  {j+1}: {lines[j].strip()}")
        output_lines.append("-" * 30)

with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\scratch\search_attachments.txt', 'w', encoding='utf-8') as f_out:
    f_out.write('\n'.join(output_lines))

print("Done")
