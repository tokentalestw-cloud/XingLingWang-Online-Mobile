# -*- coding: utf-8 -*-
import sys

def overhaul_ai():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # Define aiFindBestSummonableCard
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
    if (c.id === "SR-CAT-0026" || c.name?.includes("惡魔招財喵")) {
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

    # Replace Summon Phase AI Summoning block
    old_summon_block_start = "    const emptyFrontIdx = field.enemy_front.findIndex(u => !u);"
    old_summon_block_end = "    await sleep(800);\n\n    // 5. 對手進攻宣言與戰術佈陣階段"

    start_pos = content.find(old_summon_block_start)
    end_pos = content.find(old_summon_block_end)

    if start_pos >= 0 and end_pos >= 0:
        new_summon_block = """    // AI 單位召喚核心邏輯
    const bestSummon = window.aiFindBestSummonableCard();
    if (bestSummon) {
      const { handIdx, card, tributeUnits } = bestSummon;
      const canSummonToEnemy = xlwIsEnemySummonCard(card);
      let destZone = null;
      let destIdx = -1;

      if (canSummonToEnemy) {
        const pFront = field.player_front.findIndex(u => !u);
        const pBack = field.player_back.findIndex(u => !u);
        if (pFront >= 0 || pBack >= 0) {
          destZone = pFront >= 0 ? "player_front" : "player_back";
          destIdx = pFront >= 0 ? pFront : pBack;
        }
      } else {
        const eFront = field.enemy_front.findIndex(u => !u);
        const eBack = field.enemy_back.findIndex(u => !u);
        if (eFront >= 0 || eBack >= 0) {
          destZone = eFront >= 0 ? "enemy_front" : "enemy_back";
          destIdx = eFront >= 0 ? eFront : eBack;
        }
      }

      if (destZone && destIdx !== -1) {
        if (tributeUnits.length > 0) {
          for (const sac of tributeUnits) {
            await window.xlwEnemyTributeUnit(sac.unit, sac.zone, sac.idx);
            field[sac.zone][sac.idx] = null;
          }
          logBattle(`✨ 對手 AI 獻祭了 ${tributeUnits.length} 個單位進行獻祭召喚！`);
          render();
        }
        
        window.XLW_ENEMY.hand.splice(handIdx, 1);
        const isLyingOrc = card.id === "R-ORC-0031" || card.name?.includes("躺平獸人");
        field[destZone][destIdx] = {
          card: card,
          tapped: isLyingOrc,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: destZone
        };
        field[destZone][destIdx].card.creator = "enemy";
        logBattle(`對手召喚：${card.name} 到${destZone.startsWith("player_") ? "我方" : "對手"}${destZone.includes("front") ? "前排" : "後排"}${destIdx + 1}`);
        render();

        let starryCountered = false;
        const playerHasStarry = hand.some(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
        if (playerHasStarry) {
          const useStarry = await showXLWConfirm("【星空】手牌反制觸發", `對手召喚了【${card.name}】，是否從手牌發動【星空】進行反制（將該單位破壞並無效其效果）？`);
          if (useStarry) {
            starryCountered = true;
            const sIdx = hand.findIndex(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
            const sCard = hand.splice(sIdx, 1)[0];
            graveyard.push(sCard);
            logBattle(`✨ 我方從手牌發動了【星空】，破壞了對手剛召喚的【${card.name}】！`);
            await destroyUnit(destZone, destIdx, "enemy", false);
            render();
          }
        }

        let interruptCountered = false;
        if (!starryCountered) {
          const playerHasInterrupt = hand.some(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷你一下")));
          const hasImm = hasImmediateEffect(card);
          if (playerHasInterrupt && hasImm) {
            const useInterrupt = await showXLWConfirm("【打斷你一下】手牌反制觸發", `對手召喚了具有立即效果的【${card.name}】，是否從手牌發動【打斷你一下】進行反制（無效化其效果，但保留單位）？`);
            if (useInterrupt) {
              interruptCountered = true;
              const sIdx = hand.findIndex(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷你一下")));
              const sCard = hand.splice(sIdx, 1)[0];
              graveyard.push(sCard);
              logBattle(`✨ 我方從手牌發動了【打斷你一下】，無效化了對手剛召喚的【${card.name}】的立即效果！`);
              render();
            }
          }
        }

        if (!starryCountered && !interruptCountered) {
          await triggerAiSummonEffects(card, destZone, destIdx);
        }
        if (!starryCountered) {
          await window.checkForPlayerSummonCounters(card, destZone, destIdx, false);
        }
      }
    } else {
      logBattle("對手本回合沒有進行召喚。");
    }
    render();
    await sleep(800);\n\n    // 5. 對手進攻宣言與戰術佈陣階段"""
        content = content[:start_pos] + new_summon_block + content[end_pos + len(old_summon_block_end):]
        print("Replaced Summon Phase AI Summoning block with aiFindBestSummonableCard")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("AI Overhaul complete!")

if __name__ == '__main__':
    overhaul_ai()
