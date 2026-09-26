import re

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    text = f.read()

def extract_func(name):
    m = re.search(r'(async function\s+' + name + r'\s*\([^)]*\)\s*\{|function\s+' + name + r'\s*\([^)]*\)\s*\{)', text)
    if not m: return f'{name} not found'
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
                if depth == 0: return text[start:i+1]
        else:
            if c == str_char and text[i-1] != '\\':
                in_str = False
    return 'End not found'

out = ''
for f in ['getUnitStars', 'getUnitAtk', 'isUnitMagicImmune', 'destroyUnit', 'performSummonToSlot', 'applyPhase2Effects', 'playTravelerSummonAnimation', 'resolveUnitCombat']:
    out += extract_func(f) + '\n\n'

with open('scratch/functions.txt', 'w', encoding='utf-8') as f:
    f.write(out)
