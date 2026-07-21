with open(r"c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js", 'r', encoding='utf-8') as f:
    js_content = f.read()

import re
cat_pattern = re.findall(r'CAT-\d{4}', js_content)
print(f"Total CAT-XXXX card references in game_v8.js: {len(cat_pattern)}")
print(f"Unique references: {set(cat_pattern)}")
