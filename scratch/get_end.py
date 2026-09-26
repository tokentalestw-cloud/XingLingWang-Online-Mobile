import codecs
import re

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    text = f.read()

m = re.search(r'function performSummonToSlot\([^)]*\)\s*\{', text)
if m:
    start = m.start()
    depth = 0
    in_str = False
    str_char = ''
    for i in range(start, len(text)):
        c = text[i]
        if not in_str:
            if c in ('\'', '"', '`'):
                in_str = True
                str_char = c
            elif c == '{': depth += 1
            elif c == '}': 
                depth -= 1
                if depth == 0: 
                    func = text[start:i+1]
                    print(func[-400:])
                    break
        else:
            if c == str_char and text[i-1] != '\\':
                in_str = False
