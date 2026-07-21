with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find zone.startsWith("enemy_") or similar inside performSummonToSlot
# performSummonToSlot starts at line 4636, ends before 6614
matches = re.finditer(r'zone\.startsWith\s*\(\s*["\']enemy_["\']\s*\)', content)
for m in matches:
    line_no = content[:m.start()].count('\n') + 1
    if line_no > 4636 and line_no < 6614:
        print(f"Match found at line {line_no}")
