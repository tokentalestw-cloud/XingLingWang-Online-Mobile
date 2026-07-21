import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'drawCard' in line or 'draw' in line.lower():
            if any(x in line for x in ['function', 'action', 'ws.send', 'drawnCard']):
                safe_line = line.strip().encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                print(f"{idx+1}: {safe_line}")
