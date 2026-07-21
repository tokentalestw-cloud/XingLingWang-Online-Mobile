ws.onmessage = async (event) => {
    const data = JSON.parse(event.data);
    console.log("收到線上廣播數據:", data);
    
    if (data.type === "welcome") {
      setStatus(data.message);
    } else if (data.type === "opponent_joined") {
      // 只有在遊戲尚未開始時，才初始化新局
      if (!window.XLW_gameInProgress) {
        opponent_joined = true;
        logBattle(data.message);
        setStatus("對手已進入房間！即將開始線上起手換牌...");
        newGameMultiplayer();
      } else {
        logBattle("對手重新進入房間，正在恢復對戰...");
      }
    } else if (data.type === "opponent_rejoined") {
      logBattle(data.message);
      setStatus("對手已重新連線！正在傳送戰局狀態進行同步...");
      sendFullGameStateToOpponent();
    } else if (data.type === "opponent_rejoined_ack") {
      logBattle(data.message);
      setStatus("已成功連回遊戲！正在等待對手同步狀態...");
    } else if (data.action === "sync_game_state") {
      const s = data.state;
      if (s) {
        // 翻轉格子坐標（對手的前排是我方後排，依此類推）
        field.player_front = s.field.enemy_front;
        field.player_back = s.field.enemy_back;
        field.enemy_front = s.field.player_front;
        field.enemy_back = s.field.player_back;
        
        playerBonusScore = s.enemyBonusScore;
        enemyBonusScore = s.playerBonusScore;
        
        graveyard = s.enemyGraveyard || [];
        window.XLW_ENEMY.grave = s.graveyard || [];
        enemyGraveyard = window.XLW_ENEMY.grave;
        
        playerExileZone = s.enemyExileZone || [];
        enemyExileZone = s.playerExileZone || [];
        
        playerExtraDeck = s.enemyExtraDeck || [];
        enemyExtraDeck = s.playerExtraDeck || [];
        
        turn = s.turn;
        phase = s.phase;
        isMyTurn = !s.isMyTurn;
        
        window.XLW_ENEMY.hand = new Array(s.handCount).fill(null);
        opponent_mulligan_done = s.opponent_mulligan_done;
        
        logBattle("對戰狀態同步完成！繼續遊戲。");
        render();
      }
    } else if (data.type === "opponent_disconnected") {
      logBattle(data.message);
      setStatus(data.message);
      if (!data.temporary) {
        alert(data.message);
      } else {
        setStatus("對手暫時斷線，正在等待其重新連線...");
      }
    } else if (data.action === "coin_toss_roll") {
      showCoinRollResult(data.guess, data.result);
    } else if (data.action === "coin_toss_choice") {
      applyCoinTossChoice(data.winner_role, data.choice);
    } else if (data.action === "mulligan_confirm") {
      opponent_mulligan_done = true;
      logBattle("對手已確認起手換牌，等待我方確認。");
      await checkMulliganCompletion();
    } else if (data.action === "summon") {
      // 後端已將 zone 座標自動翻轉，所以收到時對本地來說就是 enemy_front / enemy_back
      const zone = data.zone; 
      const idx = data.idx;
      const card = data.card;
      
      // 清除對手獻祭的祭品單位
      if (data.tributes && data.tributes.length > 0) {
        data.tributes.forEach(t => {
          if (t.zone === "dummy") return;
          const unit = field[t.zone][t.idx];
          if (unit) {
            // 先處理裝備卡送入對手墓地
            if (unit.equipments && unit.equipments.length > 0) {
              unit.equipments.forEach(eqName => {
                const isTempMagic = ["削弱藥水", "振奮藥水", "塗毒", "睡眠反擊拳"].some(x => eqName.includes(x));
                if (isTempMagic) return;
                const cardObj = allCards.find(c => c && c.name === eqName) || { name: eqName, type: "magic" };
                const cloned = structuredClone(cardObj);
                cloned.type = "magic";
                window.XLW_ENEMY.grave.push(cloned);
                enemyGraveyard = window.XLW_ENEMY.grave;
                logBattle(`✨ 裝備卡 ${cloned.name} 隨著對手單位被獻祭進入對手墓地。`);
              });
              unit.equipments = [];
            }
            
            if (unit.card.name === "大耳賊" || unit.card.id === "NEU-0064") {
    if (zone.startsWith("player_")) {
      enemyBonusScore += 2;
      logBattle(`💥 大耳賊 被戰鬥破壞：對手額外獎勵 +2 ★！`);
    } else {
      playerBonusScore += 2;
      logBattle(`💥 大耳賊 被戰鬥破壞：我方額外獎勵 +2 ★！`);
    }
  }

  if (unit.card.name.includes("小旅人") || unit.card.id === "TOKEN_TRAVELER") {
              logBattle(`✨ 對手 ${unit.card.name} 作為祭品被獻祭，直接返回森林。`);
            } else {
              window.XLW_ENEMY.grave.push(unit.card);
              enemyGraveyard = window.XLW_ENEMY.grave;
            }
            field[t.zone][t.idx] = null;
          }
        });
      }

      field[zone][idx] = {
        card: card,
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: zone
      };
      // 動態遞減對手手牌數量以供顯示（僅限從手牌召喚的卡）
      if (data.fromHand !== false) {
        if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 0) {
          window.XLW_ENEMY.hand.pop();
        }
      }

      // 對手召喚時，同步觸發對我方影響的立即效果
      if (card) {
        if (card.name.includes("雪女")) {
          window.XLW_playerFrontImprisonedUntilTurn = turn;
          logBattle("雪女 效果：使我方前排戰線單位受到禁錮，直到對手下個主要階段前！");
        }
        else if (card.name.includes("座敷童子")) {
          window.XLW_playerCannotAttackOnNextTurn = true;
          logBattle("座敷童子 效果：我方下個回合將無法進行任何進攻！");
        }
        else if (card.name.includes("水瓶座")) {
          logBattle("好奇女巫 水瓶座 效果：對手召喚了 水瓶座，展示我方手牌以供檢查。");
          ws.send(JSON.stringify({
            action: "aquarius_hand_reveal",
            hand: hand
          }));
        }
        else if (card.name?.includes("戴比") || card.id === "SSR-ORC-0010") {
          window.XLW_enemyDebbieActive = true;
          logBattle("✨ 委託者 戴比 效果：對手召喚了 委託者 戴比，我方可決定對手召喚的小旅人的位置，且對手場上所有獎勵單位的戰鬥成功額外獎勵 +1！");
        }
      }

      if (card && card.id === "TOKEN_TRAVELER") {
        playTravelerSummonAnimation("#enemyForest", zone, idx);
      } else if (card && Number(card.tribute || 0) > 0) {
        playTributeSummonAnimation(zone, idx);
      } else {
        render();
      }
    } else if (data.action === "spell_chain_start") {
      spellChainStack = [{ card: data.card, owner: "opponent" }];
      if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 0) {
        window.XLW_ENEMY.hand.pop();
      }
      showSpellChainUI(spellChainStack);
      promptNextChainAction();
    } else if (data.action === "spell_chain_add") {
      spellChainStack.push({ card: data.card, owner: "opponent" });
      if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 0) {
        window.XLW_ENEMY.hand.pop();
      }
      showSpellChainUI(spellChainStack);
      promptNextChainAction();
    } else if (data.action === "spell_chain_resolve") {
      resolveLocalSpellChain();
    } else if (data.action === "equip_spell_resolved") {
      const zone = data.zone;
      const idx = data.idx;
      const spellCard = data.spellCard;
      
      const obj = field[zone]?.[idx];
      if (obj) {
        obj.equipments = obj.equipments || [];
        obj.equipments.push(spellCard.name);
        logBattle(`對手發動裝備卡 ${spellCard.name}，裝備於 ${obj.card.name} 上！`);
        
        if (spellCard.name?.includes("符咒帽") || spellCard.id === "R-0RC-0044") {
          obj.magicImmune = true;
        } else if (spellCard.name?.includes("菜刀") || spellCard.id === "R-ORC-0034") {
          obj.piercing = true;
        } else if (spellCard.name?.includes("弓箭") || spellCard.id === "R-ORC-0056") {
          obj.atkModifier = (obj.atkModifier || 0) + 1;
          obj.hasRanged = true;
        } else if (spellCard.name?.includes("戰斧牛排") || spellCard.id === "SR-ORC-0043") {
          obj.atkModifier = (obj.atkModifier || 0) + 5;
          obj.steakBonus = true;
        } else if (spellCard.name === "法術保護-護盾") {
          obj.magicImmune = true;
        }
        render();
      }
    } else if (data.action === "goat_spell_resolved") {
      const zone = data.zone;
      const idx = data.idx;
      const goatSpellCard = data.goatSpellCard;
      
      const obj = field[zone]?.[idx];
      if (obj) {
        logBattle(`對手使用 山羊術：將我方場上的 ${obj.card.name} 送入墓地，並用山羊術卡片取代！`);
        graveyard.push(obj.card); // 進入我方墓地

        const targetOwner = zone.startsWith("player_") ? "player" : "enemy";
        if (obj.equipments && obj.equipments.length > 0) {
          obj.equipments.forEach(eqName => {
            const isTempMagic = ["削弱藥水", "振奮藥水", "塗毒", "睡眠反擊拳"].some(x => eqName.includes(x));
            if (isTempMagic) return;
            const cardObj = allCards.find(c => c && c.name === eqName) || { name: eqName, type: "magic" };
            const cloned = structuredClone(cardObj);
            cloned.type = "magic";
            if (targetOwner === "player") {
              graveyard.push(cloned);
              logBattle(`✨ 裝備卡 ${cloned.name} 隨著單位變山羊進入我方墓地。`);
            } else {
              window.XLW_ENEMY.grave.push(cloned);
              enemyGraveyard = window.XLW_ENEMY.grave;
              logBattle(`✨ 裝備卡 ${cloned.name} 隨著單位變山羊進入對手墓地。`);
            }
          });
        }
        
        const goatUnitCard = structuredClone(goatSpellCard);
        goatUnitCard.type = "unit";
        goatUnitCard.attack = 3;
        goatUnitCard.score = 1;
        goatUnitCard.tribute = 0;
        goatUnitCard.faction = "中立";
        goatUnitCard.creator = "enemy"; // 標記為敵方創造
        
        obj.card = goatUnitCard;
        obj.equipments = [];
        obj.atkModifier = 0;
        obj.piercing = false;
        obj.magicImmune = false;
        obj.hasRanged = false;
        obj.steakBonus = false;
        
        render();
      }
    } else if (data.action === "aquarius_hand_reveal") {
      const oppHand = data.hand;
      window.XLW_ENEMY.hand = oppHand;
      if (window.XLW_aquariusHandResolve) {
        const resolve = window.XLW_aquariusHandResolve;
        window.XLW_aquariusHandResolve = null;
        resolve({ hand: oppHand });
      }
    } else if (data.action === "aquarius_exile_success") {
      const cardName = data.cardName;
      const hIdx = hand.findIndex(c => c && c.name === cardName);
      if (hIdx >= 0) {
        const exiledCard = hand.splice(hIdx, 1)[0];
        exileCard(exiledCard, "player");
        logBattle(`🔮 對手展示了其手牌中的 ${cardName}，我方手牌中的 ${cardName} 被除外！`);
      }
      render();
    } else if (data.action === "aquarius_complete") {
      setStatus("對手水瓶座效果結算完畢。");
      render();
    } else if (data.action === "move_unit") {
      const fromZone = data.fromZone;
      const fromIdx = data.fromIdx;
      const toZone = data.toZone;
      const toIdx = data.toIdx;
      const unit = field[fromZone][fromIdx];
      if (unit) {
        field[toZone][toIdx] = unit;
        field[fromZone][fromIdx] = null;
        logBattle(`對手進行戰術調整：將 ${unitName(unit)} 移動至其場地上`);
        render();
      }
    } else if (data.action === "swap_units") {
      const fromZone = data.fromZone;
      const fromIdx = data.fromIdx;
      const toZone = data.toZone;
      const toIdx = data.toIdx;
      const unit = field[fromZone][fromIdx];
      const targetUnit = field[toZone][toIdx];
      if (unit && targetUnit) {
        field[toZone][toIdx] = unit;
        field[fromZone][fromIdx] = targetUnit;
        logBattle(`對手進行戰術調整：將 ${unitName(unit)} 與 ${unitName(targetUnit)} 位置互換`);
        render();
      }
    } else if (data.action === "destroy_unit") {
      const zone = data.zone;
      const idx = data.idx;
      const unit = field[zone][idx];
      if (unit) {
        graveyard.push(unit.card);
        field[zone][idx] = null;
        logBattle(`\u5c0d\u624b\u7279\u6b8a\u6548\u679c\uff1a\u7834\u58bad\u6211\u65b9\u0020${unitName(unit)}\u0021`); // 對手特殊效果：破壞我方 [單位]！
        render();
      }
    } else if (data.action === "attack_declare") {
      const attZone = data.attZone;
      const attIdx = data.attIdx;
      const targetZone = data.targetZone;
      const targetIdx = data.targetIdx;
      const attacker = field[attZone][attIdx];
      if (attacker) {
        attacker.attacking = true;
        attacker.target = { zone: targetZone, idx: targetIdx };
        attacker.tapped = true;
        window.XLW_DEFENSE_RULE.playerNeedsDefense = true; // 我方防守階段標記
        const defender = field[targetZone][targetIdx];
        if (defender) {
          logBattle(`\u5c0d\u624b\u767c\u8d77\u5ba3\u544a\u9032\u653b\uff1a\u661f\u661f\u6230\u7dda${attIdx + 1}\uff0c\u5c0d\u624b\u0020${unitName(attacker)}\u0020\u6307\u5411\u6211\u65b9\u0020${unitName(defender)}`);
        } else {
          logBattle(`\u5c0d\u624b\u767c\u8d77\u7a7a\u6b04\u4f4d\u5ba3\u544a\u9032\u653b\uff1a\u661f\u661f\u6230\u7dda${attIdx + 1}\uff0c\u5c0d\u624b\u0020${unitName(attacker)}`);
        }
        render();
      }
    } else if (data.action === "attack_cancel") {
      const attZone = data.attZone;
      const attIdx = data.attIdx;
      const attacker = field[attZone][attIdx];
      if (attacker) {
        attacker.attacking = false;
        attacker.target = null;
        attacker.tapped = false;
        logBattle(`\u5c0d\u624b\u53d6\u6d88\u5ba3\u544a\u9032\u653b\uff1a\u661f\u661f\u6230\u7dda${attIdx + 1}`);
        let enemyAttackCount = 0;
        ["enemy_front", "enemy_back"].forEach(z => {
          field[z].forEach(u => {
            if (u && u.attacking) enemyAttackCount++;
          });
        });
        window.XLW_DEFENSE_RULE.playerNeedsDefense = enemyAttackCount > 0;
        render();
      }
    } else if (data.action === "cancel_all_attacks") {
      ["enemy_front", "enemy_back"].forEach(z => {
        field[z].forEach(u => {
          if (u && u.attacking) {
            u.attacking = false;
            u.target = null;
            u.tapped = false;
          }
        });
      });
      window.XLW_DEFENSE_RULE.playerNeedsDefense = false;
      logBattle("對手取消了所有進攻宣告，並返回戰術調整/召喚階段。");
      render();
    } else if (data.action === "start_defense_phase") {
      window.XLW_DEFENSE_RULE.resolving = true;
      logBattle("—— 對手防守階段開始 ——");
      setStatus("對手防守判定中，系統正在依序結算我方各星星戰線進攻...");
    } else if (data.action === "resolve_lane") {
      await xlwResolveEnemyLaneSafe(data.lane);
    } else if (data.action === "redirect_attack_target") {
      const attacker = field[data.attZone]?.[data.attIdx];
      if (attacker) {
        attacker.target = { zone: data.zone, idx: data.idx, redirected: true };
        logBattle(`✨ 對手發動 禁衛軍獸人 效果：使我方 ${attacker.card?.name || ""} 的攻擊目標轉移為對手的 禁衛軍獸人！`);
        render();
      }
    } else if (data.action === "thief_summon_sync") {
      const zone = data.zone;
      const idx = data.idx;
      
      const THIEF_CARD = allCards.find(c => c && (c.id === "NEU-0064" || c.name === "大耳賊"));
      field[zone][idx] = {
        card: structuredClone(THIEF_CARD),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: zone
      };
      
      // Also remove 大耳賊 from opponent's extra deck (which is enemyExtraDeck on our client)
      const thiefInEnemyExtra = enemyExtraDeck.find(c => c && (c.id === "NEU-0064" || c.name === "大耳賊"));
      if (thiefInEnemyExtra) {
        enemyExtraDeck.splice(enemyExtraDeck.indexOf(thiefInEnemyExtra), 1);
      }
      logBattle(`對手發動 大耳賊 效果：從其額外牌庫召喚 大耳賊 到我方 ${zone.includes("front") ? "前排" : "後排"}${idx + 1}！`);
      render();
    } else if (data.action === "add_to_hand_sync") {
      if (window.XLW_ENEMY.hand) {
        window.XLW_ENEMY.hand.push(null);
      }
      if (enemyExtraDeck && enemyExtraDeck.length > 0) {
        const idx = enemyExtraDeck.findIndex(c => c && (c.id === "R-ORC-0054" || c.name === "血戰幫狼牙棒"));
        if (idx !== -1) {
          enemyExtraDeck.splice(idx, 1);
        } else {
          enemyExtraDeck.pop();
        }
      }
      logBattle("對手從其額外牌庫將 1 張卡牌加入手牌。");
      render();
    } else if (data.action === "temp_equip_spell_resolved") {
      const targetUnit = field[data.zone]?.[data.idx];
      if (targetUnit) {
        if (!targetUnit.equipments) targetUnit.equipments = [];
        const spellNameClean = data.spellCard.name;
        if (!targetUnit.equipments.includes(spellNameClean)) {
          targetUnit.equipments.push(spellNameClean);
        }
        if (!targetUnit.tempEquips) targetUnit.tempEquips = {};
        if (spellNameClean.includes("削弱藥水") || spellNameClean.includes("睡眠反擊拳") || data.spellCard.id?.includes("0003") || data.spellCard.id?.includes("0025")) {
          targetUnit.tempEquips[spellNameClean] = data.currentTurn;
        } else if (spellNameClean.includes("振奮藥水") || data.spellCard.id?.includes("0002")) {
          targetUnit.tempEquips[spellNameClean] = data.currentTurn + 1;
        }
        logBattle(`✨ 對手發動魔法 ${spellNameClean}：賦予場上 ${targetUnit.card?.name || "單位"} 該效果作為臨時裝備。`);
        render();
      }
    } else if (data.action === "sneak_recall") {
      const key = `${data.attZone}:${data.attIdx}`;
      window.XLW_opponentSneakRecall[key] = data.recall;
    } else if (data.action === "foodball_choice") {
      const key = `${data.zone}:${data.idx}`;
      window.XLW_opponentFoodBallChoice[key] = data.trigger;
    } else if (data.action === "foodball_summon") {
      const key = `${data.zone}:${data.idx}`;
      window.XLW_opponentFoodBallSummon[key] = { zone: data.toZone, idx: data.toIdx };
    } else if (data.action === "call_game_declare") {
      window.XLW_callGameDeclared = true;
      window.XLW_callGameCondition = data.condition;
      window.XLW_callGameDeclaringPlayer = "enemy";
      window.XLW_callGameTurn = data.turn;
      
      const conditionStr = data.condition === 1 
        ? "\u5206\u6578\u52a0\u7e3d\u81f3\u5c11\u4e8c\u5341\u5206" 
        : "\u5834\u4e0a\u55ae\u4f4d\u6578\u91cf\u81f3\u5c11\u6bd4\u6575\u65b9\u591a\u56db\u500b";
      logBattle(`\u3010\u5c0d\u624b\u5ba3\u544a\u3011\u5c0d\u624b\u5ba3\u544a\u63d0\u65e9\u7d50\u675f (Call Game)\uff01\u689d\u4ef6\uff1a${conditionStr}\u3002`);
      render();
    } else if (data.action === "call_game_end") {
      triggerCallGameEnd("enemy");
    } else if (data.action === "call_game_fail") {
      window.XLW_callGameDeclared = false;
      logBattle("\u3010\u5c0d\u624b\u5ba3\u544a\u5931\u6557\u3011\u5c0d\u624b\u5148\u524d\u5ba3\u544a\u7684\u63d0\u65e9\u7d50\u675f\u689d\u4ef6\u5df2\u4e0d\u6eff\u8db3\uff0c\u5c0d\u623d\u7e7c\u7e8c\uff01");
      render();
    } else if (data.action === "end_turn") {
      // 結束階段，清理對手回合結束時到期的臨時狀態裝備
      xlwCleanExpiredTempEquips(turn);

      // 換到我方回合
      isMyTurn = true;
      turn = data.next_turn;
      window.XLW_turnSneakCount = 0;
      normalSummonUsed = false;
      tacticalSummonUsed = false;
      playerUntap();
      
      // Check Call Game resolution for player: only immediately if player does not need defense.
      let enemyHasAttackers = false;
      ["enemy_front", "enemy_back"].forEach(zone => {
        field[zone].forEach(u => {
          if (u && u.attacking) enemyHasAttackers = true;
        });
      });
      const playerNeedsDefense = window.XLW_DEFENSE_RULE.playerNeedsDefense && enemyHasAttackers;
      if (!playerNeedsDefense) {
        checkCallGameAtTurnStart(true);
        if (isGameOverFlag) return;
      }
      
      // 動態更新對手的手牌與牌庫張數（對手回補抽了 2 張）
      if (window.XLW_ENEMY.hand) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.hand.push(null);
      }
      if (window.XLW_ENEMY.deck) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.deck.pop();
      }

      await performPlayerTurnStartDraw();
      if (window.XLW_DEFENSE_RULE.playerNeedsDefense && enemyHasAttackers) {
        phase = "\u9632\u5b88\u968e\u6bb5";
        setStatus(`\u7b2c ${turn} \u56de\u5408開始，已自動抽2張。前一回合對手有進攻宣言，自動進入「防守階段」！`);
        render();
        setTimeout(() => {
          xlwResolvePlayerDefensePhase();
        }, 500);
      } else {
        const wasPending = window.XLW_DEFENSE_RULE.playerNeedsDefense;
        window.XLW_DEFENSE_RULE.playerNeedsDefense = false;
        phase = "\u53ec\u559a\u968e\u6bb5";
        setStatus(`\u7b2c ${turn} \u56de\u5408\u958b\u59cb，已自\u52d5抽2\u5f35。`);
        if (wasPending) {
          logBattle("\u6211\u65b9\u9632\u5b88階\u6bb5\u958b\u59cb\u524d，因對手無進攻單位，跳過防守階段。");
        }
        render();
      }
    } else if (data.action === "sync_deck") {
      window.XLW_ENEMY.deckName = data.deck_name;
      enemyExtraDeck = data.extra_deck || xlwInitExtraDeck(data.deck_name);
      logBattle(`對手選擇了牌組種族：${data.deck_name}`);
      render();
    } else if (data.action === "weakening_spell_resolved") {
      const zone = data.zone;
      const idx = data.idx;
      const obj = field[zone][idx];
      if (obj) {
        obj.tempAtkModifier = (obj.tempAtkModifier || 0) - 3;
        logBattle(`削弱藥水 效果：對手使場上的 ${obj.card.name} 攻擊力 -3，維持到回合結束。`);
      }
      render();

    } else if (data.action === "hannya_exile_drawn_card") {
      const exiledCard = data.exiledCard;
      const drawnCount = data.drawnCount;
      if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 0) {
        window.XLW_ENEMY.hand.pop();
      }
      enemyExileZone.push(exiledCard);
      logBattle(`憤怒的般若 效果：對手選擇將抽出的卡片 ${exiledCard.name} 除外！`);
      render();
    } else if (data.action === "hannya_reveal_drawn_card") {
      const revealedCard = data.revealedCard;
      logBattle(`智慧的般若 效果：對手選擇展示抽出的卡片：【${revealedCard.name}】！`);
      showRevealedCardModal(revealedCard, "對手");
      
      if (revealedCard.type === "unit" || revealedCard.type === "單位") {
        const prajnaSlots = [];
        for (const zone of ["player_front", "player_back"]) {
          field[zone].forEach((u, idx) => {
            if (u && u.card && u.card.name.includes("智慧的般若")) {
              prajnaSlots.push({ zone, idx, unit: u });
            }
          });
        }
        
        const angryCard = playerExtraDeck.find(c => c && (c.id === "SR-VLG-0049" || c.name.includes("憤怒的般若")));
        if (prajnaSlots.length > 0 && angryCard) {
          setTimeout(async () => {
            const yes = await showXLWConfirm("智慧的般若 進化", `對手展示了單位卡【${revealedCard.name}】，是否消耗額外區的【憤怒的般若】使場上的【智慧的般若】升級進化？`);
            if (yes) {
              let selected = prajnaSlots[0];
              if (prajnaSlots.length > 1) {
                const choices = prajnaSlots.map((h, i) => ({
                  text: `${h.zone === "player_front" ? "前排" : "後排"}${h.idx + 1} 的 智慧的般若`,
                  value: i
                }));
                const chosenIdx = await showXLWChoiceModal("選擇要進化的智慧的般若", "請選擇場上的【智慧的般若】：", choices);
                if (chosenIdx !== null && chosenIdx !== undefined) {
                  selected = prajnaSlots[chosenIdx];
                }
              }
              
              const { zone, idx, unit } = selected;
              exileCard(unit.card, "player");
              playerExtraDeck.splice(playerExtraDeck.indexOf(angryCard), 1);
              field[zone][idx] = {
                card: structuredClone(angryCard),
                tapped: false,
                attacking: false,
                target: null,
                summonedTurn: turn,
                summonedZone: zone
              };
              logBattle(`✨ 額外進化：【智慧的般若】成功升級為【憤怒的般若】！`);
              enemyBonusScore = Math.max(0, enemyBonusScore - 1);
              
              ws.send(JSON.stringify({
                action: "hannya_evolve_sync",
                zone: zone,
                idx: idx,
                angryHannya: angryCard
              }));
              render();
            }
          }, 100);
        }
      }
    } else if (data.action === "hannya_evolve_sync") {
      const zone = data.zone;
      const idx = data.idx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[zone][idx];
      if (oldUnit) {
        exileCard(oldUnit.card, "enemy");
      }
      const extraIdx = enemyExtraDeck.findIndex(c => c && (c.id === "SR-VLG-0049" || c.name.includes("憤怒的般若")));
      if (extraIdx >= 0) {
        enemyExtraDeck.splice(extraIdx, 1);
      }
      field[zone][idx] = {
        card: structuredClone(angryHannya),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: zone
      };
      logBattle(`✨ 額外進化：對手的【智慧的般若】已升級進化為【憤怒的般若】！`);
      playerBonusScore = Math.max(0, playerBonusScore - 1);
      render();
    } else if (data.action === "extra_summon_resolved") {
      const oppZone = data.fromZone;
      const oppIdx = data.fromIdx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        exileCard(oldUnit.card, "enemy");
        logBattle(`[額外召喚] 對手將場上的【般若】作為素材除外。`);
      }
      if (enemyExtraDeck.length > 0) {
        enemyExtraDeck.pop();
      }
      field[oppZone][oppIdx] = {
        card: structuredClone(angryHannya),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: oppZone
      };
      logBattle(`✨ 額外召喚：對手特殊召喚了【憤怒的般若】！`);
      playerBonusScore = Math.max(0, playerBonusScore - 1);
      logBattle(`💥 對手 憤怒的般若 效果：我方額外得分 -1 ★！`);
      render();
    } else if (data.action === "trigger_opponent_discard") {
      if (hand.length > 0) {
        const idx = Math.floor(Math.random() * hand.length);
        const discarded = hand.splice(idx, 1)[0];
        graveyard.push(discarded);
        logBattle(`🥷 變裝喵 效果：對手變裝喵偷襲成功，我方被迫隨機捨棄了手牌中的 ${discarded.name}！`);
        ws.send(JSON.stringify({
          action: "sync_discard_log",
          card_name: discarded.name
        }));
        render();
      }
    } else if (data.action === "sync_discard_log") {
      logBattle(`🥷 變裝喵 效果：對手隨機捨棄了手牌中的 ${data.card_name}！`);
      if (window.XLW_ENEMY.hand && window.XLW_ENEMY.hand.length > 0) {
        window.XLW_ENEMY.hand.pop();
      }
      render();
    } else if (data.action === "lantern_summon_single") {
      const zone = data.zone;
      const idx = data.idx;
      field[zone][idx] = {
        card: structuredClone(LITTLE_TRAVELER),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: zone
      };
      logBattle(`燈籠小鬼 效果：對手在 ${zone.includes("front") ? "前排" : "後排"}${idx + 1} 召喚了小旅人。`);
      render();
    } else if (data.action === "debbie_summon_single") {
      const zone = data.zone;
      const idx = data.idx;
      field[zone][idx] = {
        card: structuredClone(LITTLE_TRAVELER),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: zone
      };
      logBattle(`委託者 戴比 效果：對手在 ${zone.includes("front") ? "前排" : "後排"}${idx + 1} 召喚了小旅人。`);
      render();
    } else if (data.action === "field_indestructible") {
      const oppField = $("enemyField");
      if (oppField && oppField.dataset.card) {
        const fCard = JSON.parse(oppField.dataset.card);
        fCard.indestructible = true;
        oppField.dataset.card = JSON.stringify(fCard);
        logBattle(`✨ 對手場地卡【${fCard.name}】獲得了破壞抗性！`);
      }
      render();
    }
  }