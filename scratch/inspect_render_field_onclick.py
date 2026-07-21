import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_render_field = False
for idx, line in enumerate(lines):
    if 'function renderField(' in line:
        in_render_field = True
    elif in_render_field and line.startswith('}'):
        # wait, nested functions or end of renderField. Let's just track lines between 4672 and 5538.
        pass

for idx in range(4671, 5538):
    line = lines[idx]
    if 'onclick' in line:
        print(f"Line {idx+1}: {line.strip()}")
