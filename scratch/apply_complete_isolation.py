# -*- coding: utf-8 -*-
import sys

def apply_isolation():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # Locate runEnemyTurn
    start_pos = content.find('async function runEnemyTurn()')
    end_pos = content.find('// 結束我方回合，接管對手回合與我方新回合開始')

    if start_pos < 0 or end_pos < 0:
        print("ERROR: Could not find function boundaries!")
        return

    old_fn = content[start_pos:end_pos]

    new_fn = """async function runEnemyTurn() {
  window.XLW_enemySummonCountThisTurn = 0;
  window.XLW_enemyMeowToyShopUsedThisTurn = false;
  window.XLW_enemyGoatResearcherTriggeredThisTurn = false;
  window.playerReceptionistTriggeredThisTurn = false;
  window.enemyReceptionistTriggeredThisTurn = false;

  // 1. 清理過期加成與狀態
  try {
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach(u => {
        if (u && u.drunkenShroomExpiresTurn !== undefined && turn >= u.drunkenShroomExpiresTurn) {
          if (u.equipments) u.equipments = u.equipments.filter(e => e !== "酒意魔菇(+3)");
          u.drunkenShroomExpiresTurn = undefined;
          logBattle(`✨ 對手 【${u.card.name}】 的酒意魔菇加成已到期失效。`);
        }
        if (u) u.shroomMageTriggeredThisTurn = false;
      });
    }
  } catch (e) { console.warn("AI 狀態清理異常 (DrunkenShroom):", e); }

  try {
    if (window.XLW_VRCinemaActive && window.XLW_VRCinemaCaster === "enemy") {
      window.XLW_VRCinemaActive = false;
      logBattle("✨ 對手的【VR電影院】效果已結束。");
    }
  } catch (e) { console.warn("AI 狀態清理異常 (VRCinema):", e); }

  try {
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach(u => {
        if (u && u.hasFlying && u.flyingGrantedTurn !== undefined) {
          u.hasFlying = false;
          u.flyingGrantedTurn = undefined;
          logBattle(`✨ 對手 ${u.card.name} 的臨時飛行效果已到期失效。`);
        }
      });
    }
  } catch (e) { console.warn("AI 狀態清理異常 (Flying):", e); }

  try {
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach(u => {
        if (u && u.equipments && u.equipments.includes("烈陽戰士(+2)")) {
          u.equipments = u.equipments.filter(e => e !== "烈陽戰士(+2)");
          u.atkModifier = (u.atkModifier || 0) - 2;
          logBattle(`✨【烈陽戰士 獅子座】的攻擊力加成對敵方【${u.card.name}】已結束。`);
        }
        if (u && u.card && (u.card.id === "SSSR-NMS-0058" || u.card.name?.includes("烈陽戰士"))) {
          u.leoLinkedTargetUnit = null;
        }
      });
    }
  } catch (e) { console.warn("AI 狀態清理異常 (LeoBuff):", e); }

  try {
    for (const z of ["player_front", "player_back"]) {
      field[z].forEach(u => {
        if (u && u.equipments && u.equipments.includes("冰霜法師(-3)")) {
          u.equipments = u.equipments.filter(e => e !== "冰霜法師(-3)");
          logBattle(`✨【冰霜法師 水瓶座】的星數減免對我方【${u.card.name}】已結束。`);
        }
      });
    }
  } catch (e) { console.warn("AI 狀態清理異常 (AquariusDebuff):", e); }

  if (window.XLW_ENEMY.running) {
    console.warn("AI runEnemyTurn was flagged running. Resetting flag and executing turn.");
  }
  window.XLW_ENEMY.running = true;

  try {
    // 2. 提早結束檢測 (Call Game)
    try {
      const playerHasAttackers = field["player_front"].concat(field["player_back"]).some(u => u && u.attacking);
      const enemyNeedsDefense = window.XLW_DEFENSE_RULE.enemyNeedsDefense && playerHasAttackers;
      if (!enemyNeedsDefense) {
        checkCallGameAtTurnStart(false);
        if (isGameOverFlag) return;
      }
    } catch (e) { console.warn("AI Call Game 檢測異常:", e); }

    const enemyDeckName = window.XLW_ENEMY?.deckName || "對手";
    logBattle(`—— 對手回合開始 (${enemyDeckName}) ——`);
    setStatus(`對手回合：${enemyDeckName} 正在進行整備抽牌...`);
    await sleep(700);

    // 3. 整備階段：對手單位轉正
    try {
      untapEnemy();
    } catch (e) { console.warn("AI untapEnemy 異常:", e); }
    
    // 4. 對手抽 2 張
    try {
      const enemyDrawn = [];
      for (let i = 0; i < 2; i++) {
        if (window.XLW_ENEMY.deck && window.XLW_ENEMY.deck.length) {
          enemyDrawn.push(window.XLW_ENEMY.deck.pop());
        }
      }
      
      const hasSmartPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name?.includes("智慧的般若"));
      const hasAngryPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name?.includes("憤怒的般若"));

      if (enemyDrawn.length > 0) {
        if (hasAngryPrajna) {
          const exileIdx = Math.floor(Math.random() * enemyDrawn.length);
          const exiledCard = enemyDrawn[exileIdx];
          exileCard(exiledCard, "enemy");
          logBattle(`憤怒的般若 效果：對手選擇將抽出的卡片 ${exiledCard.name} 除外！`);
          enemyDrawn.forEach((c, idx) => {
            if (idx !== exileIdx) window.XLW_ENEMY.hand.push(c);
          });
        } else if (hasSmartPrajna) {
          let revealIdx = 0;
          if (enemyDrawn.length > 1) {
            const hasSpell = enemyDrawn.some(c => c && c.type !== "unit" && c.type !== "單位");
            const hasUnit = enemyDrawn.some(c => c && (c.type === "unit" || c.type === "單位"));
            if (hasSpell && hasUnit) {
              revealIdx = enemyDrawn.findIndex(c => c && c.type !== "unit" && c.type !== "單位");
            } else {
              revealIdx = Math.floor(Math.random() * enemyDrawn.length);
            }
          }
          const revealedCard = enemyDrawn[revealIdx];
          enemyDrawn.forEach(c => window.XLW_ENEMY.hand.push(c));
          logBattle(`智慧的般若 效果：對手選擇展示抽出的卡片：【${revealedCard.name}】！`);
          showRevealedCardModal(revealedCard, "對手");
        } else {
          enemyDrawn.forEach(c => window.XLW_ENEMY.hand.push(c));
        }
      }
      logBattle("對手整備：對手抽卡結算完成，單位全體轉正。");
      render();
    } catch (e) { console.warn("AI 抽牌階段異常:", e); }

    // 5. 迷路的尋寶小旅人
    try {
      let aiTravelerIndices = [];
      (window.XLW_ENEMY.hand || []).forEach((c, idx) => {
        if (c && (c.id === "NEU-0010" || c.name?.includes("迷路的尋寶小旅人") || c.name?.includes("尋寶小旅人"))) {
          aiTravelerIndices.push(idx);
        }
      });
      if (aiTravelerIndices.length > 0) {
        for (let idx = aiTravelerIndices.length - 1; idx >= 0; idx--) {
          const hIdx = aiTravelerIndices[idx];
          const card = window.XLW_ENEMY.hand.splice(hIdx, 1)[0];
          enemyExileZone.push(card);
          enemyBonusScore += 1;
          logBattle("✨ 對手 迷路的尋寶小旅人 效果觸發：回合開始抽牌時除外手牌，對手獲得 +1★ 獎勵！");
        }
        renderScore();
        render();
      }
    } catch (e) { console.warn("AI 小旅人手牌判定異常:", e); }

    await sleep(700);

    // 6. 防守階段結算
    try {
      const playerHasAttackers = field["player_front"].concat(field["player_back"]).some(u => u && u.attacking);
      if (window.XLW_DEFENSE_RULE.enemyNeedsDefense && playerHasAttackers) {
        phase = "防守階段";
        setStatus("對手回合：正在自動結算對手防守階段對決...");
        render();
        await xlwResolveEnemyDefensePhaseSafe();
      } else {
        window.XLW_DEFENSE_RULE.enemyNeedsDefense = false;
        logBattle("對手防守階段開始前，因我方無進攻單位，跳過防守階段。");
      }
    } catch (e) { console.warn("AI 防守階段異常:", e); }

    // 7. 召喚階段
    phase = "召喚階段";
    setStatus(`對手回合：${enemyDeckName} 正在進行召喚階段...`);
    render();
    
    // 特殊前置效果觸發 (Leo, Aquarius, Nurse, ViceDirector, TourGuide, Beibei, Nezhul, etc.)
    try {
      // 獅子座
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u.card && (u.card.id === "SSSR-NMS-0058" || u.card.name?.includes("烈陽戰士")) && !window.isUnitSilenced(u, z, i) && u.leoEffectUsedTurn !== turn) {
            let target = null;
            let maxAtk = -999;
            for (const tz of ["enemy_front", "enemy_back"]) {
              field[tz].forEach((tu, ti) => {
                if (tu && tu !== u) {
                  const atk = getUnitAtk(tu, tz, ti);
                  if (atk > maxAtk) { maxAtk = atk; target = tu; }
                }
              });
            }
            if (target) {
              target.atkModifier = (target.atkModifier || 0) + 2;
              target.equipments = target.equipments || [];
              target.equipments.push("烈陽戰士(+2)");
              u.leoEffectUsedTurn = turn;
              logBattle(`✨ 對手 烈陽戰士 獅子座 效果：使對手單位【${target.card.name}】攻擊力 +2！`);
              render();
            }
          }
        });
      }
    } catch (e) { console.warn("AI 獅子座前置效果異常:", e); }

    try { await checkCrazyFanSummon(); } catch (e) { console.warn("AI 瘋狂粉絲前置效果異常:", e); }
    try { await xlwCheckBananaMarquisMovement(false); } catch (e) { console.warn("AI 香蕉侯爵前置效果異常:", e); }
    try { await window.xlwResolveTurnStartEffects(false); } catch (e) { console.warn("AI 回合開始觸發效果異常:", e); }

    // AI 魔法卡發動 (獨立保護，絕不影響單位召喚)
    try {
      await aiPlayMagicCardsSummonPhase();
    } catch (e) {
      console.error("AI 召喚階段發動魔法卡異常:", e);
    }

    // 8. ★ AI 單位召喚核心邏輯 (Core Summoning) ★
    let bestSummon = null;
    try {
      bestSummon = window.aiFindBestSummonableCard();
    } catch (e) {
      console.error("AI 召喚檢索出錯:", e);
    }

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
            const playerHasInterrupt = hand.some(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷你一下")));
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
      logBattle("🤖【對手 AI】主要召喚階段未打出常規單位，準備進行戰術佈陣與進攻調整。");
    }
    render();
    await sleep(800);

    // 9. ★ 進攻宣言與戰術佈陣階段 ★
    const aiWentFirst = (window.XLW_coinTossFirstGo === false);
    const isAiFirstTurn = aiWentFirst && (turn === 1);

    if (countdownActive && countdownRemaining === 1) {
      logBattle("對手最後一回合：只能進行召喚階段，跳過戰術佈陣與進攻宣言。");
      window.XLW_DEFENSE_RULE.playerNeedsDefense = false;
      render();
      await sleep(800);
    } else if (isAiFirstTurn) {
      logBattle("對手第一回合（先手）：只能進行召喚階段，跳過戰術佈陣與進攻宣言。");
      window.XLW_DEFENSE_RULE.playerNeedsDefense = false;
      render();
      await sleep(800);
    } else {
      try { await checkPopulationCap(false); } catch (e) {}
      phase = "進攻宣言";
      setStatus(`對手回合：${enemyDeckName} 正在進行進攻檢視與宣告...`);
      render();

      let opponentAttackCount = 0;
      try {
        const playerHasYeshu = ["player_front", "player_back"].some(pz => 
          field[pz].some(u => u && u.card && (u.card.id === "SR-ART-0026" || u.card.name?.includes("和平使者 耶叔")))
        );
        if (playerHasYeshu) {
          logBattle("和平使者 耶叔 效果生效：對手本回合無法進行任何進攻！");
        } else if (window.XLW_enemyCannotAttackThisTurn) {
          logBattle("座敷童子/和平巨人 效果生效：本回合對手無法進行任何進攻！");
        } else {
          for (let i = 0; i < 5; i++) {
            const enemyAttacker = field.enemy_front[i] || field.enemy_back[i];
            const enemyAttackerZone = field.enemy_front[i] ? "enemy_front" : "enemy_back";
            if (!enemyAttacker || enemyAttacker.tapped) continue;
            if (window.XLW_isShieldUnit(enemyAttacker)) continue;
            const enemyAttackerCard = enemyAttacker.card || enemyAttacker;
            const enemyCannotAttack = (enemyAttackerCard.effect_text && enemyAttackerCard.effect_text.includes("無法進攻")) ||
                                       (enemyAttackerCard.keywords && enemyAttackerCard.keywords.includes("無法進攻"));
            if (enemyCannotAttack) continue;
            if (window.xlwIsAttackBlockedByClea(enemyAttackerZone, i)) continue;

            const hasRanged = (enemyAttacker.card && (
              (enemyAttacker.card.keywords && enemyAttacker.card.keywords.includes("遠程")) ||
              (enemyAttacker.card.effect_text && enemyAttacker.card.effect_text.includes("遠程"))
            ));
            const isBoarKnight = enemyAttacker.card && (enemyAttacker.card.id === "R-NMS-0061" || enemyAttacker.card.name?.includes("野豬騎士"));
            const targetsBackFirst = hasRanged || isBoarKnight;

            let targetZone = null;
            if (targetsBackFirst) {
              targetZone = field.player_back[i] ? "player_back" : (field.player_front[i] ? "player_front" : null);
            } else {
              targetZone = field.player_front[i] ? "player_front" : (field.player_back[i] ? "player_back" : null);
            }

            if (!targetZone) continue;
            
            const targetDefender = field[targetZone][i];
            if (window.XLW_isShieldUnit(targetDefender)) continue;
            if (targetDefender && isUnitAttackProtected(targetZone, i)) continue;
            
            if (targetDefender && !isMultiplayer) {
              const favorable = checkAiAttackFavorability(enemyAttacker, enemyAttackerZone, i, targetDefender, targetZone, i);
              if (!favorable) {
                logBattle(`對手 AI 判定：星星戰線 ${i + 1}，我方防守較強，放棄進攻以保存實力。`);
                continue;
              }
            }

            enemyAttacker.attacking = true;
            enemyAttacker.target = { zone: targetZone, idx: i };
            opponentAttackCount++;
            logBattle(`⚔️ 對手進攻宣言：星星戰線${i + 1}，對手 ${unitName(enemyAttacker)} 指向我方 ${unitName(targetDefender)}`);
          }
        }
      } catch (errAtk) {
        console.error("AI 進攻宣告階段異常:", errAtk);
      }

      window.XLW_DEFENSE_RULE.playerNeedsDefense = opponentAttackCount > 0;
      logBattle(`—— 對手回合階段完成，已宣告 ${opponentAttackCount} 條星星戰線進攻。 ——`);
      render();
      await sleep(700);

      // 10. ★ 戰術佈陣階段 (Tactical Phase & Fallback Summon) ★
      if (opponentAttackCount === 0) {
        phase = "戰術佈陣";
        setStatus(`對手回合：${enemyDeckName} 正在進行戰術佈陣與單位佈局...`);
        render();

        try {
          await aiPerformTacticalMovement();
        } catch (e) {
          console.warn("AI 戰術移動異常:", e);
        }

        const emptyFrontIdx = field.enemy_front.findIndex(u => !u);
        const emptyBackIdx = field.enemy_back.findIndex(u => !u);
        const hasEmptySlot = emptyFrontIdx >= 0 || emptyBackIdx >= 0;

        if (hasEmptySlot) {
          let bestTactical = null;
          try {
            bestTactical = window.aiFindBestSummonableCard();
          } catch (e) {
            console.error("AI 戰術階段召喚檢索出錯:", e);
          }

          const destZone = emptyFrontIdx >= 0 ? "enemy_front" : "enemy_back";
          const destIdx = emptyFrontIdx >= 0 ? emptyFrontIdx : emptyBackIdx;

          if (bestTactical && destZone && destIdx !== -1) {
            const { handIdx, card, tributeUnits } = bestTactical;
            if (tributeUnits && tributeUnits.length > 0) {
              for (const sac of tributeUnits) {
                try { await window.xlwEnemyTributeUnit(sac.unit, sac.zone, sac.idx); } catch (e) {}
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
            window.XLW_enemySummonCountThisTurn = (window.XLW_enemySummonCountThisTurn || 0) + 1;
            logBattle(`🤖【對手 AI 戰術佈陣召喚】打出單位【${card.name}】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}！`);
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
                const playerHasInterrupt = hand.some(c => c && (c.id === "R-NMG-0022" || c.id === "SSSR-NMG-0022" || c.name?.includes("打斷你一下")));
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
            } catch (errTacticalTrig) {
              console.error("AI 戰術召喚觸發效果出錯:", errTacticalTrig);
            }
          } else {
            // 保底召喚小旅人
            field[destZone][destIdx] = {
              card: structuredClone(LITTLE_TRAVELER),
              tapped: false,
              attacking: false,
              target: null,
              summonedTurn: turn,
              summonedZone: destZone
            };
            logBattle(`🤖【對手 AI 戰術佈陣】無常規單位可召喚，強制特召【小旅人】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);
            try {
              playTravelerSummonAnimation("#enemyForest", destZone, destIdx);
            } catch (e) {}

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
                  logBattle(`✨ 我方從手牌發動了【星空】，破壞了對手剛召喚的【小旅人】！`);
                  await destroyUnit(destZone, destIdx, "enemy", false);
                  render();
                }
              }
              if (!starryCountered) {
                await window.checkForPlayerSummonCounters(LITTLE_TRAVELER, destZone, destIdx, false);
              }
            } catch (errTravelerTrig) {
              console.error("小旅人觸發效果出錯:", errTravelerTrig);
            }
          }
          render();
          await sleep(1000);
        }
      }
    }

    // 11. 回合結束清理與手牌超限處理
    try {
      if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 10) {
        const excessCount = window.XLW_ENEMY.hand.length - 10;
        logBattle(`⚠️ 對手回合結束，手牌達 ${window.XLW_ENEMY.hand.length} 張（超過 10 張限額），自動除外 ${excessCount} 張手牌。`);
        for (let i = 0; i < excessCount; i++) {
          const idx = Math.floor(Math.random() * window.XLW_ENEMY.hand.length);
          const card = window.XLW_ENEMY.hand[idx];
          window.XLW_ENEMY.hand.splice(idx, 1);
          enemyExileZone.push(card);
          logBattle(`對手將手牌中的【${card ? card.name : "未知卡牌"}】置於除外區。`);
        }
        render();
        await sleep(500);
      }
    } catch (e) { console.warn("AI 手牌超限處理異常:", e); }

  } catch (errTop) {
    console.error("對手 AI 頂層運行出錯:", errTop);
    logBattle(`對手行動出錯: ${errTop.message}`);
  } finally {
    window.XLW_ENEMY.running = false;
  }
}
"""

    content = content[:start_pos] + new_fn + content[end_pos:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Full isolation rewrite applied to runEnemyTurn successfully!")

if __name__ == '__main__':
    apply_isolation()
