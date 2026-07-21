import re

with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

fns = [
    'performSummonToSlot',
    'triggerAiSummonEffects',
    'castSpell',
    'getUnitAtk',
    'isUnitMagicImmune',
    'isUnitIndestructible',
    'resolveUnitCombat',
    'runNeutralEndPhaseEffects',
    'performPlayerTurnStartDraw'
]

for fn in fns:
    match = re.search(r'(async\s+)?function\s+' + fn + r'\b', content)
    if match:
        line_no = content[:match.start()].count('\n') + 1
        print(f"{fn}: line {line_no}")
    else:
        print(f"{fn}: NOT FOUND")
