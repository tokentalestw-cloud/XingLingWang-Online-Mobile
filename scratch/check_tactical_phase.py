with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'phase\s*===\s*["\']戰術佈陣["\']', content)
for m in matches:
    line_no = content[:m.start()].count('\n') + 1
    print(f"Match found at line {line_no}")
