# -*- coding: utf-8 -*-
import sys

def apply_guaranteed_summon():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # Update index.html cache-buster first
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    if 'game_v8.js?v=' in idx_content:
        import re
        idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=8.55-guaranteed-ai-summon-20260719', idx_content)
        open(idx_path, 'w', encoding='utf-8').write(idx_content)
        print("Updated index.html script tag with cache-buster v=8.55-guaranteed-ai-summon-20260719")

    # Locate runEnemyTurn in game_v8.js
    start_pos = content.find('async function runEnemyTurn()')
    end_pos = content.find('// 結束我方回合，接管對手回合與我方新回合開始')

    if start_pos < 0 or end_pos < 0:
        print("ERROR: Boundaries not found!")
        return

    old_fn = content[start_pos:end_pos]

    # Look for Summon Phase block in old_fn
    summon_marker_start = "    // 8. ★ AI 單位召喚核心邏輯 (Core Summoning) ★"
    summon_marker_end = "    // 9. ★ 進攻宣言與戰術佈陣階段 ★"

    sm_s = old_fn.find(summon_marker_start)
    sm_e = old_fn.find(summon_marker_end)

    if sm_s < 0 or sm_e < 0:
        print("ERROR: Summon marker not found!")
        return

    new_summon_block = """    // 8. ★ AI 單位召喚核心邏輯 (Core Summoning & 100% Guaranteed Placement) ★
    let bestSummon = null;
    try {
      bestSummon = window.aiFindBestSummonableCard();
    } catch (e) {
      console.error("AI 召喚檢索出錯:", e);
    }

    let destZone = null;
    let destIdx = -1;

    if (bestSummon) {
      const { handIdx, card, tributeUnits } = bestSummon;
      const canSummonToEnemy = xlwIsEnemySummonCard(card);

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
        if (tributeUnits && tributeUnits.length > 0) {
          for (const sac of tributeUnits) {
            try { await window.xlwEnemyTributeUnit(sac.unit, sac.zone, sac.idx); } catch (e) {}
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
        window.XLW_enemySummonCountThisTurn = (window.XLW_enemySummonCountThisTurn || 0) + 1;
        logBattle(`🤖【對手 AI 召喚】打出單位【${card.name}】到${destZone.startsWith("player_") ? "我方" : "對手"}${destZone.includes("front") ? "前排" : "後排"}${destIdx + 1}！`);
        render();
        await sleep(1000);

        try {
          let starryCountered = false;
          const playerHasStarry = hand.some(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
          if (playerHasStarry) {
            const useStarry = await showXLWConfirm("【星空】手牌反制觸發", `對手召喚了【${card.name}】，是否從手牌發動【星空】進行反制？`);
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
            const playerHasInterrupt = hand.some(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷抗性/打斷你一下")));
            const hasImm = hasImmediateEffect(card);
            if (playerHasInterrupt && hasImm) {
              const useInterrupt = await showXLWConfirm("【打斷你一下】手牌反制觸發", `對手召喚了具有立即效果的【${card.name}】，是否發動【打斷你一下】無效其效果？`);
              if (useInterrupt) {
                interruptCountered = true;
                const sIdx = hand.findIndex(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷你一下")));
                const sCard = hand.splice(sIdx, 1)[0];
                graveyard.push(sCard);
                logBattle(`✨ 我方發動【打斷你一下】，無效化了對手剛召喚的【${card.name}】的立即效果！`);
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
        } catch (errSummonTrig) {
          console.error("AI 召喚觸發卡牌效果出錯:", errSummonTrig);
        }
      }
    } else {
      // 保底機制：若手牌無常規免祭品單位，自動特殊召喚【小旅人】建立戰線！
      const eFront = field.enemy_front.findIndex(u => !u);
      const eBack = field.enemy_back.findIndex(u => !u);
      if (eFront >= 0 || eBack >= 0) {
        destZone = eFront >= 0 ? "enemy_front" : "enemy_back";
        destIdx = eFront >= 0 ? eFront : eBack;

        field[destZone][destIdx] = {
          card: structuredClone(LITTLE_TRAVELER),
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: destZone
        };
        field[destZone][destIdx].card.creator = "enemy";
        window.XLW_enemySummonCountThisTurn = (window.XLW_enemySummonCountThisTurn || 0) + 1;
        logBattle(`🤖【對手 AI 召喚】手牌無免祭品單位，自動戰術特召【小旅人】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}！`);
        try { playTravelerSummonAnimation("#enemyForest", destZone, destIdx); } catch (e) {}
        render();
        await sleep(1000);

        try {
          let starryCountered = false;
          const playerHasStarry = hand.some(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
          if (playerHasStarry) {
            const useStarry = await showXLWConfirm("【星空】手牌反制觸發", `對手召喚了【小旅人】，是否從手牌發動【星空】進行反制？`);
            if (useStarry) {
              starryCountered = true;
              const sIdx = hand.findIndex(c => c && (c.id === "ART-0020" || c.name?.includes("星空")));
              const sCard = hand.splice(sIdx, 1)[0];
              graveyard.push(sCard);
              logBattle(`✨ 我方從手牌發動了【星空】，破壞了對手的【小旅人】！`);
              await destroyUnit(destZone, destIdx, "enemy", false);
              render();
            }
          }
          if (!starryCountered) {
            await window.checkForPlayerSummonCounters(LITTLE_TRAVELER, destZone, destIdx, false);
          }
        } catch (e) {}
      }
    }
    render();
    await sleep(800);

"""

    updated_fn = old_fn[:sm_s] + new_summon_block + old_fn[sm_e:]
    content = content[:start_pos] + updated_fn + content[end_pos:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Guaranteed 100% AI summon logic applied to game_v8.js successfully!")

if __name__ == '__main__':
    apply_guaranteed_summon()
