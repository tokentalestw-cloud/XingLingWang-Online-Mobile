import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'broadcast' in line or 'send_json' in line or 'websocket_endpoint' in line or 'manager' in line:
        print(f"Line {idx+1}: {line.strip()}")
