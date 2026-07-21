with open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'resolveUnitCombat' in line or 'triggerSneakAttackSuccessEffects' in line or 'applyCombatSuccessReward' in line:
        print(f"Line {idx + 1}: {line.strip()}")
