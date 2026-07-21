import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'XLW_turnTappedUnits' in line or 'XLW_opponentDoubleClawChoice' in line or 'XLW_opponentSneakRecall' in line:
        print(f"Line {idx+1}: {line.strip()}")
