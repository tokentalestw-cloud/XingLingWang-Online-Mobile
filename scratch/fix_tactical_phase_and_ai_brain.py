# -*- coding: utf-8 -*-
import sys

def fix_ai():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # Replacement for aiFindBestSummonableCard
    old_helper_start = "window.aiFindBestSummonableCard = function() {"
    old_helper_end = "  return candidates[0];\n};"

    start_pos = content.find(old_helper_start)
    end_pos = content.find(old_helper_end)

    if start_pos >= 0 and end_pos >= 0:
        new_helper = """window.aiFindBestSummonableCard = function() {
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
  aiAvailableUnits.sort((a, b) => {
    const atkA = parseInt(a.unit.card.attack, 10) || 0;
    const atkB = parseInt(b.unit.card.attack, 10) || 0;
    return atkA - atkB;
  });

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
    const numAtk = parseInt(c.attack, 10) || 0;
    if (cost <= 0) {
      candidates.push({ handIdx, card: c, tributeUnits: [], priority: 100 + numAtk });
    } else if (aiAvailableUnits.length >= cost) {
      candidates.push({ handIdx, card: c, tributeUnits: aiAvailableUnits.slice(0, cost), priority: 50 + numAtk });
    }
  });

  if (candidates.length === 0) return null;

  // 排序選出最高優先度的卡牌
  candidates.sort((a, b) => (b.priority || 0) - (a.priority || 0));
  return candidates[0];
};"""
        content = content[:start_pos] + new_helper + content[end_pos + len(old_helper_end):]
        print("Updated aiFindBestSummonableCard with safe NaN-free priorities")

    # Replace Tactical Phase summoning block
    tactical_search_start = "        // AI 執行戰術佈陣移動：將弱小/高分脆皮單位移回後排"
    tactical_search_end = "    // 對手 AI 調色盤 結束階段效果"

    t_start = content.find(tactical_search_start)
    t_end = content.find(tactical_search_end)

    if t_start >= 0 and t_end >= 0:
        new_tactical = """        // AI 執行戰術佈陣移動：將弱小/高分脆皮單位移回後排
        await aiPerformTacticalMovement();

        const emptyFrontIdx = field.enemy_front.findIndex(u => !u);
        const emptyBackIdx = field.enemy_back.findIndex(u => !u);
        const hasEmptySlot = emptyFrontIdx >= 0 || emptyBackIdx >= 0;

        if (hasEmptySlot) {
          const bestTactical = window.aiFindBestSummonableCard();
          const destZone = emptyFrontIdx >= 0 ? "enemy_front" : "enemy_back";
          const destIdx = emptyFrontIdx >= 0 ? emptyFrontIdx : emptyBackIdx;

          if (bestTactical && destZone && destIdx !== -1) {
            const { handIdx, card, tributeUnits } = bestTactical;
            if (tributeUnits.length > 0) {
              for (const sac of tributeUnits) {
                await window.xlwEnemyTributeUnit(sac.unit, sac.zone, sac.idx);
                field[sac.zone][sac.idx] = null;
              }
              logBattle(`✨ 對手 AI 戰術階段獻祭了 ${tributeUnits.length} 個單位！`);
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
            logBattle(`對手進行戰術佈陣召喚：${card.name} 到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);

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
          } else {
            field[destZone][destIdx] = {
              card: structuredClone(LITTLE_TRAVELER),
              tapped: false,
              attacking: false,
              target: null,
              summonedTurn: turn,
              summonedZone: destZone
            };
            logBattle(`對手無單位可召喚，戰術強制召喚：小旅人 到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);
            playTravelerSummonAnimation("#enemyForest", destZone, destIdx);

            let starryCountered = false;
            const playerHasStarry = hand.some(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
            if (playerHasStarry) {
              const useStarry = await showXLWConfirm("【星空】手牌反制觸發", `對手召喚了【小旅人】，是否從手牌發動【星空】進行反制？`);
              if (useStarry) {
                starryCountered = true;
                const sIdx = hand.findIndex(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
                const sCard = hand.splice(sIdx, 1)[0];
                graveyard.push(sCard);
                logBattle(`✨ 我方從手牌發動了【星空】，破壞了對手剛召喚的【小旅人】！`);
                await destroyUnit(destZone, destIdx, "enemy", false);
                render();
              }
            }
            if (!starryCountered) {
              await window.checkForPlayerSummonCounters(LITTLE_TRAVELER, destZone, destIdx, false);
            }
          }
          render();
          await sleep(800);
        }
      }
    }

"""
        content = content[:t_start] + new_tactical + content[t_end:]
        print("Replaced Tactical Phase AI summoning block with clean aiFindBestSummonableCard and Chinese strings")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fix applied successfully!")

if __name__ == '__main__':
    fix_ai()
