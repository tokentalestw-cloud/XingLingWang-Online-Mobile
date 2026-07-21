with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.finditer(r'function\s+canSummonCard\b', content)
for m in matches:
    line_no = content[:m.start()].count('\n') + 1
    print(f"canSummonCard defined at line {line_no}")

matches_cost = re.finditer(r'getCardTributeCost\b', content)
for m in matches_cost:
    line_no = content[:m.start()].count('\n') + 1
    print(f"getCardTributeCost referenced at line {line_no}")
