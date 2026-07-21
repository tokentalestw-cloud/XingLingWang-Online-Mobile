with open(r'c:\Users\a2132\Documents\星靈王\XingLingWang_v7_fixed\static\game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

keywords = ['function castSpell', 'function getUnitAtk', 'function destroyUnit', 'function applyCombatSuccessReward', 'function playerUntap', 'function renderField', 'double_claw_choice', 'R-CAT-0040']

for kw in keywords:
    print(f"=== Matches for '{kw}' ===")
    for i, line in enumerate(lines):
        if kw in line:
            print(f"Line {i+1}: {line.strip()}")
            # Print a few surrounding lines if matching a function
            start = max(0, i - 2)
            end = min(len(lines), i + 8)
            for j in range(start, end):
                print(f"  {j+1}: {lines[j].strip()}")
            print("-" * 20)
