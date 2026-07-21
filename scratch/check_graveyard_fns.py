with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'function\s+\w*(Grave|Graveyard)\w*\b', content, re.IGNORECASE)
for m in matches:
    line_no = content[:m.start()].count('\n') + 1
    print(f"Graveyard function defined at line {line_no}: {m.group(0)}")
