import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = -1
end = -1
for idx, line in enumerate(lines):
    if 'function showExtraDeckDetailModal' in line:
        start = idx + 1
    elif start != -1 and line.startswith('// ===== 22. 本地戰局存檔'):
        end = idx
        break

print(f"Start: {start}, End: {end}")
