# -*- coding: utf-8 -*-
import sys

def upgrade_ai():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # 1. Add aiFindBestSummonableCard helper function
    ai_helper = """
// AI 最佳可召喚卡牌尋找函式
window.aiFindBestSummonableCard = function() {
  const enemyHand = window.XLW_ENEMY?.hand || [];
  const enemyGrave = window.XLW_ENEMY?.grave || [];
  const enemyExile = enemyExileZone || [];

  const aiAvailableUnits = [];
  for (const z of ["enemy_front", "enemy_back"]) {
    field[z].forEach((u, i) => {
      if (u && u.card) aiAvailableUnits.push({ zone: z, idx: i, unit: u });
    });
  }
  // 依攻擊力低至高排序作為獻祭素材
  aiAvailableUnits.sort((a, b) => getUnitAtk(a.unit, a.zone, a.idx) - getUnitAtk(b.unit, b.zone, b.idx));

  const candidates = [];

  enemyHand.forEach((c, handIdx) => {
    if (!c || (c.type !== "unit" && c.type !== "單位")) return;

    // 檢查卡牌效果是否禁止常規召喚（如：只能通過...效果召喚）
    const effectText = c.effect_text || "";
    if (effectText.includes("只能通") || effectText.includes("只能透過")) return;

    // 特殊卡牌條件限制
    if ((c.id === "SR-CAT-0026" || c.name?.includes("惡魔招財喵"))) {
      const catCount = enemyGrave.filter(cg => cg && (cg.deck === "喵喵賊" || cg.faction === "喵喵賊" || (cg.id && String(cg.id).toLowerCase().includes("cat")))).length;
      if (catCount < 3) return;
    }
    if (c.id === "R-FMS-0030" || c.id === "SSR-FMS-0030" || c.name?.includes("高塔101號")) {
      if (!window.xlwCheckMahjongCombo(false, "小四喜")) return;
    }
    if (c.id === "SR-FMS-0036" || c.name?.includes("麻祖")) {
      const hasHu = enemyExile.some(ex => ex && (ex.id === "SR-FMS-0016" || ex.id === "R-FMS-0017" || ex.name?.includes("大三元") || ex.name?.includes("小四喜")));
      if (!hasHu) return;
    }

    const cost = getCardTributeCost(c);
    if (cost <= 0) {
      candidates.push({ handIdx, card: c, tributeUnits: [], priority: 100 + Number(c.attack || 0) });
    } else if (aiAvailableUnits.length >= cost) {
      candidates.push({ handIdx, card: c, tributeUnits: aiAvailableUnits.slice(0, cost), priority: 50 + Number(c.attack || 0) });
    }
  });

  if (candidates.length === 0) return null;

  // 排序選出最高優先度的卡牌
  candidates.sort((a, b) => b.priority - a.priority);
  return candidates[0];
};
"""

    if "window.aiFindBestSummonableCard =" not in content:
        content = content.replace("async function runEnemyTurn() {", ai_helper + "\nasync function runEnemyTurn() {")
        print("Added aiFindBestSummonableCard helper function")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("AI Brain Upgrade script completed")

if __name__ == '__main__':
    upgrade_ai()
