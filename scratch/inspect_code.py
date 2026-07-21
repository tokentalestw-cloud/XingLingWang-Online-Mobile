import os

filepath = 'static/game_v8.js'
queries = [
    'xlwOnPlayerUnitTapped',
    'xlwCheckNegativeEnergyMeowUpgrade',
    'xlwCheckDoubleClawMeowUpgrade',
    'xlwCheckManagerMeowUpgrade',
    'xlwCleanDoubleClawBonus',
    'XLW_teasingStickMoveActive',
    'XLW_turnTappedUnits',
    'XLW_turnCombatWins',
    'XLW_turnExtraSummonsCount'
]

if os.path.exists(filepath):
    print("File size:", os.path.getsize(filepath))
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print("Total lines:", len(lines))
    for query in queries:
        found = []
        for idx, line in enumerate(lines):
            if query in line:
                found.append((idx + 1, line.strip()))
        print(f"\nQuery: '{query}' -> found {len(found)} matches:")
        for line_num, content in found[:15]:
            print(f"  Line {line_num}: {content}")
else:
    print("File not found")
