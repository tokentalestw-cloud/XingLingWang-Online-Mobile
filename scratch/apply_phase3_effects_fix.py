# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    try:
        code = open(filepath, encoding="utf-8").read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    def safe_replace(label, target, replacement):
        nonlocal code
        if target in code:
            code = code.replace(target, replacement)
            print(f"[{label}] Replaced successfully.")
        elif replacement in code:
            print(f"[{label}] Already replaced (skipped).")
        else:
            print(f"[{label}] Warning: target not found!")

    # 10. runEnemyTurn Lingsao Movement Trigger (AI/Enemy Side)
    target_ai_lingsao = """        // AI 恐怖小丑 (R-VLG-0048) 效果發動
        const enemyGrave = window.XLW_ENEMY.grave || [];"""

    replacement_ai_lingsao = """        // AI 靈騷獸人 (R-ORC-0030) 效果發動
        const hasLingsao = ["enemy_front", "enemy_back"].some(z => {
          return field[z].some((u, i) => u && u.card && (u.card.id === "R-ORC-0030" || u.card.name?.includes("靈騷獸人")) && !window.isUnitSilenced(u, z, i));
        });
        if (hasLingsao && !window.XLW_enemyLingsaoTriggeredThisTurn) {
          const orcUnits = [];
          for (const z of ["enemy_front", "enemy_back"]) {
            field[z].forEach((u, i) => {
              if (u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
                orcUnits.push({ zone: z, idx: i, unit: u });
              }
            });
          }
          const emptySlots = window.xlwGetEmptyEnemySlots();
          if (orcUnits.length > 0 && emptySlots.length > 0) {
            window.XLW_enemyLingsaoTriggeredThisTurn = true;
            const target = orcUnits[Math.floor(Math.random() * orcUnits.length)];
            const dest = emptySlots[Math.floor(Math.random() * emptySlots.length)];
            field[dest.zone][dest.idx] = target.unit;
            field[target.zone][target.idx] = null;
            logBattle(`✨ 對手 靈騷獸人 效果：將【${target.unit.card.name}】移動到 ${dest.zone.includes("front") ? "前排" : "後排"}${dest.idx + 1}！`);
            render();
          }
        }

        // AI 恐怖小丑 (R-VLG-0048) 效果發動
        const enemyGrave = window.XLW_ENEMY.grave || [];"""

    safe_replace("runEnemyTurn Lingsao Movement Trigger (AI/Enemy Side)", target_ai_lingsao, replacement_ai_lingsao)

    # Save the modified code back to static/game_v8.js
    open(filepath, "w", encoding="utf-8").write(code)
    print("All Phase 3 changes written successfully.")

if __name__ == '__main__':
    main()
