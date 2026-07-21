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

    # 1. Custom Helpers
    target_helpers = "window.xlwPlayerTributeUnit = async function(unit, zone, idx) {"
    replacement_helpers = """window.xlwIsShenaOnField = function() {
  for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
    const list = field[z];
    for (let i = 0; i < 5; i++) {
      const u = list[i];
      if (u && u.card && (u.card.id === "SSSR-NMS-0027" || u.card.name?.includes("星娜")) && !window.isUnitSilenced(u, z, i)) {
        return true;
      }
    }
  }
  return false;
};

window.xlwIsGoatBlocked = function(isPlayerCaster) {
  const oppZones = isPlayerCaster ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
  for (const z of oppZones) {
    const list = field[z];
    for (let i = 0; i < 5; i++) {
      const u = list[i];
      if (u && u.card && (u.card.id === "SSSR-NMS-0028" || u.card.name?.includes("魔羯座") || u.card.name?.includes("山羊勇者")) && !window.isUnitSilenced(u, z, i)) {
        return true;
      }
    }
  }
  return false;
};

window.xlwIsAttackBlockedByClea = function(zone, idx) {
  const isPlayer = zone.startsWith("player_");
  const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
  const oppUnit = field[oppFrontZone][idx];
  if (oppUnit && oppUnit.card && (oppUnit.card.id === "SSSR-NMS-0033" || oppUnit.card.name?.includes("克蕾") || oppUnit.card.name?.includes("參謀")) && !window.isUnitSilenced(oppUnit, oppFrontZone, idx)) {
    return true;
  }
  return false;
};

window.xlwTriggerKururuEffect = async function(isPlayerOwner) {
  const oppHand = isPlayerOwner ? window.XLW_ENEMY.hand : hand;
  const oppDeck = isPlayerOwner ? window.XLW_ENEMY.deck : deck;
  const count = (oppHand || []).filter(Boolean).length;
  if (count === 0) {
    logBattle("小女魔導士庫路路 效果：對手手牌為空，無須重洗。");
    return;
  }
  
  oppHand.forEach(c => {
    if (c) oppDeck.push(c);
  });
  
  if (isPlayerOwner) {
    window.XLW_ENEMY.hand = [];
  } else {
    hand.splice(0, hand.length);
  }
  
  shuffle(oppDeck);
  
  const drawCount = Math.min(count, oppDeck.length);
  for (let i = 0; i < drawCount; i++) {
    const drawn = oppDeck.pop();
    if (isPlayerOwner) {
      window.XLW_ENEMY.hand.push(drawn);
    } else {
      hand.push(drawn);
    }
  }
  
  logBattle(`✨ 小女魔導士庫路路 效果：使對手將所有手牌（共 ${count} 張）洗回牌庫，並重新抽取了 ${drawCount} 張手牌！`);
  render();
  if (isMultiplayer) {
    sendFullGameStateToOpponent();
  }
};

window.xlwReturnUnitToHand = async function(zone, idx) {
  const unit = field[zone][idx];
  if (!unit) return;
  const isPlayer = zone.startsWith("player_");
  
  // 寶寶獸人 (C-ORC-0012) 回手牌前得分效果
  if (unit.card && (unit.card.id === "C-ORC-0012" || unit.card.id === "R-ORC-0012" || unit.card.id === "SSR-ORC-0012" || unit.card.name?.includes("寶寶獸人")) && !window.isUnitSilenced(unit, zone, idx)) {
    if (isPlayer) {
      playerBonusScore += 1;
      logBattle("✨ 寶寶獸人 離場回手效果：我方額外獎勵 +1★！");
    } else {
      enemyBonusScore += 1;
      logBattle("✨ 對手 寶寶獸人 離場回手效果：對手額外獎勵 +1★！");
    }
    renderScore();
  }
  
  const card = unit.card;
  if (isPlayer) {
    hand.push(card);
  } else {
    if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
    window.XLW_ENEMY.hand.push(card);
  }
  field[zone][idx] = null;
  render();

  // 獸人姑姑 (R-ORC-0047) 效果
  const sidePrefix = isPlayer ? "player_" : "enemy_";
  const hasAunt = [sidePrefix + "front", sidePrefix + "back"].some(z => {
    return field[z].some((u, i) => {
      return u && u.card && (u.card.id === "R-ORC-0047" || u.card.name?.includes("姑姑")) && !window.isUnitSilenced(u, z, i);
    });
  });
  
  if (hasAunt && !window.XLW_orcAuntTriggeredThisTurn) {
    const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
    const playableOrcs = myHand.filter(c => c && c.type === "unit" && (c.faction === "獸人" || c.id?.includes("ORC")) && Number(c.tribute || 0) === 0);
    
    if (playableOrcs.length > 0) {
      const emptySlots = isPlayer ? window.xlwGetEmptyPlayerSlots() : window.xlwGetEmptyEnemySlots();
      if (emptySlots.length > 0) {
        window.XLW_orcAuntTriggeredThisTurn = true;
        if (isPlayer) {
          const confirm = await showXLWConfirm("獸人姑姑 效果發動", "偵測到有獸人單位回手牌，是否發動【獸人姑姑】效果從手牌額外特殊召喚一隻 0 祭品獸人？");
          if (confirm) {
            const choices = playableOrcs.map((c, i) => ({ text: `${c.name}`, value: i }));
            const chosenIdx = await showXLWChoiceModal("選擇額外召喚的獸人", "選擇一隻獸人特殊召喚：", choices);
            if (chosenIdx !== null && chosenIdx !== undefined) {
              const newCard = playableOrcs[chosenIdx];
              const handIdx = hand.indexOf(newCard);
              if (handIdx >= 0) hand.splice(handIdx, 1);
              
              selectedHandForSummon = hand.indexOf(newCard);
              window.XLW_bypassNormalSummonLimit = true;
              setStatus(`【獸人姑姑 召喚】請點選我方一個空格特殊召喚【${newCard.name}】！`);
              render();
              await new Promise(r => { window.XLW_summonPlacementResolve = r; });
            }
          }
        } else {
          const newCard = playableOrcs[0];
          const handIdx = myHand.indexOf(newCard);
          if (handIdx >= 0) myHand.splice(handIdx, 1);
          await window.xlwSpecialSummonUnit(newCard, false);
          logBattle(`✨ 對手 獸人姑姑 效果：額外特殊召喚了【${newCard.name}】！`);
          render();
        }
      }
    }
  }
};

window.xlwAddGraveyardCardToHand = function(card, isPlayer) {
  const grave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
  const gIdx = grave.indexOf(card);
  if (gIdx >= 0) {
    grave.splice(gIdx, 1);
  }
  if (isPlayer) {
    hand.push(card);
  } else {
    if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
    window.XLW_ENEMY.hand.push(card);
  }
  
  if (card && (card.id === "R-ORC-0049" || card.name?.includes("獸人弟弟"))) {
    if (isPlayer) {
      playerBonusScore += 2;
      logBattle("✨ 獸人弟弟 墓地回手效果：我方額外獎勵 +2★！");
    } else {
      enemyBonusScore += 2;
      logBattle("✨ 對手 獸人弟弟 墓地回手效果：對手額外獎勵 +2★！");
    }
    renderScore();
  }
  render();
};

window.xlwTriggerOrcUntapSynergy = function(isPlayer) {
  if (window.XLW_untapSynergyGuard) return;
  window.XLW_untapSynergyGuard = true;
  try {
    const zones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
    let hasTappedSteakAx = false;
    
    zones.forEach(z => {
      field[z].forEach(u => {
        if (u && u.tapped && u.equipments && u.equipments.some(eq => eq.includes("戰斧") || eq.includes("牛排")) && !window.isUnitSilenced(u, z, field[z].indexOf(u))) {
          hasTappedSteakAx = true;
        }
      });
    });
    
    if (hasTappedSteakAx) {
      zones.forEach(z => {
        field[z].forEach((u, i) => {
          if (u && u.tapped && u.equipments && u.equipments.some(eq => eq.includes("戰斧") || eq.includes("牛排")) && !window.isUnitSilenced(u, z, i)) {
            u.tapped = false;
            logBattle(`✨ 激動獸人的牛排戰斧 效果：由於場上有其他獸人轉正，【${u.card.name}】也跟著轉正！`);
          }
        });
      });
      render();
    }
  } finally {
    window.XLW_untapSynergyGuard = false;
  }
};

window.xlwTriggerMaskTaunt = async function(isPlayerEndPhase) {
  const tauntZones = isPlayerEndPhase ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
  const oppFrontZone = isPlayerEndPhase ? "player_front" : "enemy_front";
  
  for (const tz of tauntZones) {
    for (let col = 0; col < 5; col++) {
      const u = field[tz][col];
      if (u && u.equipments && u.equipments.some(eq => eq.includes("面具")) && !window.isUnitSilenced(u, tz, col)) {
        const oppUnit = field[oppFrontZone][col];
        if (oppUnit && !oppUnit.tapped) {
          logBattle(`✨ 挑釁獸人的面具 效果：在結束階段強迫正前方的【${oppUnit.card.name}】向其發起進攻！`);
          const attZone = oppFrontZone;
          const defZone = tz;
          const defenderOwner = isPlayerEndPhase ? "enemy" : "player";
          const combatRes = await resolveUnitCombat(attZone, col, defZone, col, defenderOwner);
          logBattle(`挑釁進攻結果：${combatRes}`);
          render();
        }
      }
    }
  }
};

window.xlwTriggerSubsituteNinja = async function(defZone, defIdx) {
  const defender = field[defZone][defIdx];
  if (!defender || !defender.card) return;
  const isOrc = defender.card.faction === "獸人" || defender.card.id?.includes("ORC");
  if (!isOrc || window.isUnitSilenced(defender, defZone, defIdx)) return;
  
  const isPlayer = defZone.startsWith("player_");
  const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
  
  const ninjaIdx = myHand.findIndex(c => c && (c.id === "R-ORC-0045" || c.name?.includes("替身忍法")));
  if (ninjaIdx < 0) return;
  
  const playableOrcs = myHand.filter(c => c && c.type === "unit" && (c.faction === "獸人" || c.id?.includes("ORC")) && Number(c.tribute || 0) === 0);
  if (playableOrcs.length === 0) return;
  
  if (isPlayer) {
    const confirm = await showXLWConfirm("獸人替身忍法 效果觸發", `偵測到我方獸人【${defender.card.name}】被選為攻擊目標！是否從手牌發動【獸人替身忍法】？`);
    if (confirm) {
      const spellCard = myHand.splice(ninjaIdx, 1)[0];
      graveyard.push(spellCard);
      
      await window.xlwReturnUnitToHand(defZone, defIdx);
      
      const choices = playableOrcs.map((c, i) => ({ text: `${c.name}`, value: i }));
      const chosenIdx = await showXLWChoiceModal("選擇替換召喚的獸人", "請選擇一個 0 祭品獸人召喚至原位：", choices);
      if (chosenIdx !== null && chosenIdx !== undefined) {
        const newCard = playableOrcs[chosenIdx];
        const handIdx = hand.indexOf(newCard);
        if (handIdx >= 0) hand.splice(handIdx, 1);
        
        field[defZone][defIdx] = {
          card: newCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: defZone
        };
        logBattle(`✨ 獸人替身忍法：將【${defender.card.name}】回收至手牌，並在原位置特殊召喚了【${newCard.name}】！`);
        render();
      }
    }
  } else {
    if (Math.random() < 0.5) {
      const spellCard = myHand.splice(ninjaIdx, 1)[0];
      window.XLW_ENEMY.grave.push(spellCard);
      
      await window.xlwReturnUnitToHand(defZone, defIdx);
      
      const newCard = playableOrcs[0];
      const handIdx = myHand.indexOf(newCard);
      if (handIdx >= 0) myHand.splice(handIdx, 1);
      
      field[defZone][defIdx] = {
        card: newCard,
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: defZone
      };
      logBattle(`✨ 對手 獸人替身忍法：將【${defender.card.name}】回收至手牌，並在原位置特殊召喚了【${newCard.name}】！`);
      render();
    }
  }
};

window.xlwPlayerTributeUnit = async function(unit, zone, idx) {"""

    safe_replace("Helpers", target_helpers, replacement_helpers)

    # 2. checkCallGameAtTurnStart update
    target_callgame = """function checkCallGameAtTurnStart(isMyTurnStarting) {
  if (!window.XLW_callGameDeclared) return;"""
    
    replacement_callgame = """function checkCallGameAtTurnStart(isMyTurnStarting) {
  if (window.xlwIsShenaOnField()) {
    window.XLW_callGameDeclared = false;
    return;
  }
  if (!window.XLW_callGameDeclared) return;"""

    safe_replace("checkCallGameAtTurnStart", target_callgame, replacement_callgame)

    # 3. AI call game end check
    target_ai_callgame = """    // 6. 對手 AI 結束階段宣告提早結束檢測
    if (!window.XLW_callGameDeclared && !window.XLW_callGameNegatedThisTurn) {"""
    
    replacement_ai_callgame = """    // 6. 對手 AI 結束階段宣告提早結束檢測
    if (!window.xlwIsShenaOnField() && !window.XLW_callGameDeclared && !window.XLW_callGameNegatedThisTurn) {"""

    safe_replace("AI call game end check", target_ai_callgame, replacement_ai_callgame)

    # 4. Player call game end check
    target_player_callgame = """  if (!window.XLW_callGameDeclared && (canDeclare1 || canDeclare2)) {"""
    
    replacement_player_callgame = """  if (!window.xlwIsShenaOnField() && !window.XLW_callGameDeclared && (canDeclare1 || canDeclare2)) {"""

    safe_replace("Player call game end check", target_player_callgame, replacement_player_callgame)

    # 5. Player direct Goat Spell check
    target_direct_goat = """  } else if (card.name.includes("山羊術")) {
    let hasAnyUnit = false;"""
    
    replacement_direct_goat = """  } else if (card.name.includes("山羊術")) {
    if (window.xlwIsGoatBlocked(true)) {
      setStatus("敵方場上有【山羊勇者魔羯座】，我方被限制無法施展山羊術！");
      return;
    }
    let hasAnyUnit = false;"""

    safe_replace("Player direct Goat Spell check", target_direct_goat, replacement_direct_goat)

    # 6. Player chain Goat Spell check
    target_chain_goat = """  // 2. 山羊術：使場上1單位變為山羊
  else if (card.name.includes("山羊術")) {
    let hasAnyUnit = false;"""
    
    replacement_chain_goat = """  // 2. 山羊術：使場上1單位變為山羊
  else if (card.name.includes("山羊術")) {
    if (window.xlwIsGoatBlocked(true)) {
      setStatus("敵方場上有【山羊勇者魔羯座】，我方被限制無法施展山羊術！");
      return;
    }
    let hasAnyUnit = false;"""

    safe_replace("Player chain Goat Spell check", target_chain_goat, replacement_chain_goat)

    # 7. AI counter Goat Spell check
    target_ai_goat = """  const goatIdx = hand.findIndex(c => c && (c.id === "SSR-NMG-0012" || c.name?.includes("山羊術")));
  if (goatIdx >= 0 && attacker && !isUnitMagicImmune(attacker, attZone, lane)) {"""
    
    replacement_ai_goat = """  const goatIdx = hand.findIndex(c => c && (c.id === "SSR-NMG-0012" || c.name?.includes("山羊術")));
  if (goatIdx >= 0 && attacker && !isUnitMagicImmune(attacker, attZone, lane) && !window.xlwIsGoatBlocked(false)) {"""

    safe_replace("AI counter Goat Spell check", target_ai_goat, replacement_ai_goat)

    # 8. performSummonToSlot card checks
    target_summon_checks = """    if (!immediateEffectNegated && card) {
      if (card.id === "VRT-0009" || card.name?.includes("打卡的酒醉鄉民")) {"""

    replacement_summon_checks = """    if (!immediateEffectNegated && card) {
      // SSSR-NMS-0031 小女魔導士庫路路
      if (card.id === "SSSR-NMS-0031" || card.name?.includes("庫路路") || card.name?.includes("魔導士")) {
        await window.xlwTriggerKururuEffect(zone.startsWith("player_"));
      }
      // SSSR-NMS-0053 幻想巨人 雙魚座
      if (card.id === "SSSR-NMS-0053" || card.name?.includes("雙魚座")) {
        if (zone.startsWith("player_")) {
          window.XLW_playerPiscesActive = true;
          logBattle("✨ 幻想巨人 雙魚座 效果發動：本次對決我方的所有戰術階段將不再被跳過！");
        } else {
          window.XLW_enemyPiscesActive = true;
          logBattle("✨ 對手 幻想巨人 雙魚座 效果發動：本次對決對手的所有戰術階段將不再被跳過！");
        }
      }
      // C-ORC-0012 寶寶獸人
      if (card.id === "C-ORC-0012" || card.id === "R-ORC-0012" || card.id === "SSR-ORC-0012" || card.name?.includes("寶寶獸人")) {
        if (zone.startsWith("player_")) {
          playerBonusScore += 1;
          logBattle("✨ 寶寶獸人 立即效果：我方額外獎勵 +1★！");
        } else {
          enemyBonusScore += 1;
          logBattle("✨ 對手 寶寶獸人 立即效果：對手額外獎勵 +1★！");
        }
        renderScore();
      }
      // C-ORC-0016 駭獸人
      if (card.id === "C-ORC-0016" || card.id === "ORC-0016" || card.name?.includes("駭獸人")) {
        const isPlayer = zone.startsWith("player_");
        const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
        const oppBackZone = isPlayer ? "enemy_back" : "player_back";
        const targetUnit = field[oppFrontZone][idx] || field[oppBackZone][idx];
        if (targetUnit) {
          const emptySlots = [];
          for (const z of [oppFrontZone, oppBackZone]) {
            field[z].forEach((u, col) => {
              if (col !== idx && u === null) {
                emptySlots.push({ zone: z, idx: col });
              }
            });
          }
          if (emptySlots.length > 0) {
            const chosen = emptySlots[Math.floor(Math.random() * emptySlots.length)];
            const originalZone = field[oppFrontZone][idx] ? oppFrontZone : oppBackZone;
            field[originalZone][idx] = null;
            field[chosen.zone][chosen.idx] = targetUnit;
            logBattle(`✨ 駭獸人 立即效果：將正前方的敵方單位【${targetUnit.card.name}】移至 ${chosen.zone === oppFrontZone ? "前排" : "後排"}${chosen.idx + 1}！`);
            render();
          } else {
            logBattle("駭獸人 立即效果：對手場上其他星星戰線無空位，無法移動！");
          }
        }
      }
      // SR-ORC-0053 憤怒的駭獸人
      if (card.id === "SR-ORC-0053" || card.name?.includes("憤怒的駭獸人")) {
        const isPlayer = zone.startsWith("player_");
        const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
        const units = [];
        oppZones.forEach(z => {
          field[z].forEach((u, col) => {
            if (u) {
              units.push(u);
              field[z][col] = null;
            }
          });
        });
        if (units.length > 0) {
          const allSlots = [];
          oppZones.forEach(z => {
            for (let col = 0; col < 5; col++) {
              allSlots.push({ zone: z, idx: col });
            }
          });
          shuffle(allSlots);
          units.forEach((u, uIdx) => {
            const slot = allSlots[uIdx];
            field[slot.zone][slot.idx] = u;
          });
          logBattle(`✨ 憤怒的駭獸人 立即效果：打亂對手場上所有單位的位置！`);
          render();
        }
      }
      // ORC-0013 媽咪獸人
      if (card.id === "ORC-0013" || card.name?.includes("媽咪獸人")) {
        const isPlayer = zone.startsWith("player_");
        const myZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
        const myOrcs = [];
        myZones.forEach(z => {
          field[z].forEach((u, col) => {
            if (u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC")) && (u !== field[zone][idx])) {
              myOrcs.push({ zone: z, idx: col, unit: u });
            }
          });
        });
        if (myOrcs.length > 0) {
          if (isPlayer) {
            const choices = myOrcs.map((item, cIdx) => ({
              text: `${item.unit.card.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`,
              value: cIdx
            }));
            const chosen = await showXLWChoiceModal("媽咪獸人 效果", "選擇一個我方獸人單位收回手牌：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = myOrcs[chosen];
              logBattle(`✨ 媽咪獸人 效果：將我方場上的【${target.unit.card.name}】收回手牌。`);
              await window.xlwReturnUnitToHand(target.zone, target.idx);
            }
          } else {
            const target = myOrcs[Math.floor(Math.random() * myOrcs.length)];
            logBattle(`✨ 對手 媽咪獸人 效果：將對手場上的【${target.unit.card.name}】收回手牌。`);
            await window.xlwReturnUnitToHand(target.zone, target.idx);
          }
        } else {
          logBattle("媽咪獸人 效果：場上無其他我方獸人單位，無法觸發效果。");
        }
      }
      // R-ORC-0017 獸人女王 金納斯
      if (card.id === "R-ORC-0017" || card.id === "R-ORC-0017-金" || card.name?.includes("金納斯")) {
        const isPlayer = zone.startsWith("player_");
        const myZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
        if (isPlayer) {
          while (true) {
            const myOrcs = [];
            myZones.forEach(z => {
              field[z].forEach((u, col) => {
                if (u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC")) && (u !== field[zone][idx])) {
                  myOrcs.push({ zone: z, idx: col, unit: u });
                }
              });
            });
            if (myOrcs.length === 0) break;
            const choices = myOrcs.map((item, cIdx) => ({
              text: `${item.unit.card.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`,
              value: cIdx
            }));
            choices.push({ text: "✨ 完成選擇並結束效果", value: "done" });
            const chosen = await showXLWChoiceModal("獸人女王 金納斯 效果", "請選擇收回手牌的獸人單位（可多選）：", choices);
            if (chosen === null || chosen === undefined || chosen === "done") break;
            const target = myOrcs[chosen];
            logBattle(`✨ 獸人女王 金納斯 效果：將我方場上的【${target.unit.card.name}】收回手牌。`);
            await window.xlwReturnUnitToHand(target.zone, target.idx);
          }
        } else {
          const myOrcs = [];
          myZones.forEach(z => {
            field[z].forEach((u, col) => {
              if (u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC")) && (u !== field[zone][idx])) {
                myOrcs.push({ zone: z, idx: col, unit: u });
              }
            });
          });
          for (const target of myOrcs) {
            if (Math.random() < 0.5) {
              logBattle(`✨ 對手 獸人女王 金納斯 效果：將對手場上的【${target.unit.card.name}】收回手牌。`);
              await window.xlwReturnUnitToHand(target.zone, target.idx);
            }
          }
        }
      }
      // R-ORC-0001 札克
      if (card.id === "R-ORC-0001" || card.name?.includes("札克")) {
        const isPlayer = zone.startsWith("player_");
        const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
        const oppBackZone = isPlayer ? "enemy_back" : "player_back";
        const targetZone = field[oppFrontZone][idx] === null ? oppFrontZone : (field[oppBackZone][idx] === null ? oppBackZone : null);
        if (targetZone) {
          const travelerCard = allCards.find(c => c && (c.id === "TOKEN_TRAVELER" || c.name.includes("小旅人"))) || { id: "TOKEN_TRAVELER", name: "小旅人", type: "unit", tribute: 0, attack: "1", score: 1 };
          field[targetZone][idx] = {
            card: travelerCard,
            tapped: false,
            attacking: false,
            target: null,
            summonedTurn: turn,
            summonedZone: targetZone
          };
          logBattle(`✨ 札克 立即效果：為對手在 ${targetZone === oppFrontZone ? "前排" : "後排"}${idx + 1} 召喚了一個【小旅人】！`);
          render();
        } else {
          logBattle("札克 立即效果：對手正前方及後方皆滿，無法召喚小旅人。");
        }
      }
      // R-ORC-0014 獸人挑戰者
      if (card.id === "R-ORC-0014" || card.name?.includes("挑戰者")) {
        const isPlayer = zone.startsWith("player_");
        const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
        const candidates = [];
        field[oppFrontZone].forEach((u, col) => {
          if (u && col !== idx) candidates.push({ zone: oppFrontZone, idx: col, unit: u });
        });
        if (candidates.length > 0) {
          if (isPlayer) {
            const choices = candidates.map((item, cIdx) => ({
              text: `${item.unit.card.name} (前排${item.idx + 1})`,
              value: cIdx
            }));
            const chosen = await showXLWChoiceModal("獸人挑戰者 效果", "請選擇要拉到其正前方的敵方前排單位：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = candidates[chosen];
              logBattle(`✨ 獸人挑戰者 效果：拉動對手【${target.unit.card.name}】至其正前方！`);
              await moveOrPushUnitToSlot(target.zone, target.idx, oppFrontZone, idx);
            }
          } else {
            const target = candidates[Math.floor(Math.random() * candidates.length)];
            logBattle(`✨ 對手 獸人挑戰者 效果：拉動我方【${target.unit.card.name}】至其正前方！`);
            await moveOrPushUnitToSlot(target.zone, target.idx, oppFrontZone, idx);
          }
        }
      }
      // R-ORC-0041 士氣獸人
      if (card.id === "R-ORC-0041" || card.name?.includes("士氣獸人")) {
        const isPlayer = zone.startsWith("player_");
        const myZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
        const tappedOrcs = [];
        myZones.forEach(z => {
          field[z].forEach((u, col) => {
            if (u && u.tapped && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC")) && u !== field[zone][idx]) {
              tappedOrcs.push({ zone: z, idx: col, unit: u });
            }
          });
        });
        if (tappedOrcs.length > 0) {
          if (isPlayer) {
            const choices = tappedOrcs.map((item, cIdx) => ({
              text: `${item.unit.card.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`,
              value: cIdx
            }));
            const chosen = await showXLWChoiceModal("士氣獸人 效果", "選擇一個被橫置的我方獸人單位轉正：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = tappedOrcs[chosen];
              target.unit.tapped = false;
              logBattle(`✨ 士氣獸人 效果：使我方場上的【${target.unit.card.name}】轉正！`);
              window.xlwTriggerOrcUntapSynergy(true);
              render();
            }
          } else {
            const target = tappedOrcs[Math.floor(Math.random() * tappedOrcs.length)];
            target.unit.tapped = false;
            logBattle(`✨ 對手 士氣獸人 效果：使對手場上的【${target.unit.card.name}】轉正！`);
            window.xlwTriggerOrcUntapSynergy(false);
            render();
          }
        }
      }
      // R-ORC-0059 懸賞獸人
      if (card.id === "R-ORC-0059" || card.name?.includes("懸賞獸人")) {
        const isPlayer = zone.startsWith("player_");
        const extraDeck = isPlayer ? window.XLW_playerExtraDeck : (window.XLW_enemyExtraDeck || []);
        const targetIdx = extraDeck.findIndex(c => c && (c.id === "R-ORC-0058" || c.name?.includes("懸賞令")));
        if (targetIdx >= 0) {
          const bountyCard = extraDeck.splice(targetIdx, 1)[0];
          if (isPlayer) {
            hand.push(bountyCard);
            logBattle(`✨ 懸賞獸人 立即效果：從額外區將【懸賞令】加入手牌！`);
          } else {
            if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
            window.XLW_ENEMY.hand.push(bountyCard);
            logBattle(`✨ 對手 懸賞獸人 立即效果：從其額外區將【懸賞令】加入手牌！`);
          }
          render();
        }
      }
      // ORC-0009 / SSR-ORC-0009 獸人王 加爾帝
      if (card.id === "ORC-0009" || card.id === "SSR-ORC-0009" || card.name?.includes("加爾帝")) {
        const isPlayer = zone.startsWith("player_");
        const frontZone = isPlayer ? "player_front" : "enemy_front";
        const backZone = isPlayer ? "player_back" : "enemy_back";
        if (zone === backZone && field[frontZone][idx] === null) {
          const travelerCard = allCards.find(c => c && (c.id === "TOKEN_TRAVELER" || c.name.includes("小旅人"))) || { id: "TOKEN_TRAVELER", name: "小旅人", type: "unit", tribute: 0, attack: "1", score: 1 };
          field[frontZone][idx] = {
            card: travelerCard,
            tapped: false,
            attacking: false,
            target: null,
            summonedTurn: turn,
            summonedZone: frontZone
          };
          logBattle(`✨ 獸人王 加爾帝 立即效果：召喚了一個【小旅人】至其正前方！`);
          render();
        }
      }

      if (card.id === "VRT-0009" || card.name?.includes("打卡的酒醉鄉民")) {"""

    safe_replace("performSummonToSlot card checks", target_summon_checks, replacement_summon_checks)

    # 9. Player manual attack Taunt/Clea block
    target_manual_atk = """function selectPlayerAttacker(zone, idx) {
  if (phase !== "進攻宣言") return;
  const unit = field[zone][idx];"""

    replacement_manual_atk = """function selectPlayerAttacker(zone, idx) {
  if (phase !== "進攻宣言") return;
  if (window.xlwIsAttackBlockedByClea(zone, idx)) {
    setStatus("該單位正前方有【魔王女參謀 克蕾】，被其壓制無法宣告進攻！");
    return;
  }
  const unit = field[zone][idx];"""

    safe_replace("Player manual attack Taunt/Clea block", target_manual_atk, replacement_manual_atk)

    # 10. Player auto-attack Clea block
    target_auto_atk = """    const actualZone = field.player_front[i] === playerAttacker ? "player_front" : "player_back";
    // 禁錮狀態的單位可以進攻"""

    replacement_auto_atk = """    const actualZone = field.player_front[i] === playerAttacker ? "player_front" : "player_back";
    if (window.xlwIsAttackBlockedByClea(actualZone, i)) continue;
    // 禁錮狀態的單位可以進攻"""

    safe_replace("Player auto-attack Clea block", target_auto_atk, replacement_auto_atk)

    # 11. AI auto-attack Clea block
    target_ai_atk = """          const enemyCannotAttack = (enemyAttackerCard.effect_text && enemyAttackerCard.effect_text.includes("無法進攻")) ||
                                     (enemyAttackerCard.keywords && enemyAttackerCard.keywords.includes("無法進攻"));
          if (enemyCannotAttack) continue;"""

    replacement_ai_atk = """          const enemyCannotAttack = (enemyAttackerCard.effect_text && enemyAttackerCard.effect_text.includes("無法進攻")) ||
                                     (enemyAttackerCard.keywords && enemyAttackerCard.keywords.includes("無法進攻"));
          if (enemyCannotAttack) continue;
          if (window.xlwIsAttackBlockedByClea(enemyAttackerZone, i)) continue;"""

    safe_replace("AI auto-attack Clea block", target_ai_atk, replacement_ai_atk)

    # 12. canSummonCard checks
    target_cansummon = """function canSummonCard(card, isPlayer) {
  if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {"""

    replacement_cansummon = """function canSummonCard(card, isPlayer) {
  if (card.id === "SSSR-NMS-0034" || card.name?.includes("火野貝")) {
    const zones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
    const hasUnits = zones.some(z => field[z].some(u => u !== null));
    if (hasUnits) {
      if (isPlayer) {
        setStatus("【召喚限制】海中的干貝 火野貝 只能在場上沒有 any 我方單位時才能召喚！");
      }
      return false;
    }
  }
  if (card.id === "SR-ORC-0026" || card.id === "SSR-ORC-0026" || card.name?.includes("奈祖爾")) {
    const zones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
    let tappedOrcCount = 0;
    zones.forEach(z => {
      field[z].forEach((u, i) => {
        if (u && u.tapped && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC")) && !window.isUnitSilenced(u, z, i)) {
          tappedOrcCount++;
        }
      });
    });
    const ok = tappedOrcCount >= 2;
    if (!ok && isPlayer) {
      setStatus("【召喚限制】永鬥神 奈祖爾 需要我方場上有 2 個或以上橫置的獸人單位！");
    }
    return ok;
  }
  if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {"""

    safe_replace("canSummonCard checks", target_cansummon, replacement_cansummon)

    # 13. applyCombatSuccessReward triggers
    target_success_rewards = """  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    replacement_success_rewards = """  if ((cid === "ORC-0002" || name?.includes("背刺獸人")) && isAttacker) {
    baseReward += 2;
    hasRewardEffect = true;
  }
  if ((cid === "ORC-0003" || cid === "SSR-ORC-0003" || name?.includes("菜刀哥")) && isAttacker) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if ((cid === "ORC-0004" || name?.includes("破甲獸人")) && isAttacker) {
    baseReward += 2;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0001" || name?.includes("札克")) && isAttacker) {
    baseReward += 2;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0007" || name?.includes("鐵獸人")) && !isAttacker) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0014" || name?.includes("挑戰者")) && isAttacker) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0024" || name?.includes("爆破獸人")) && isAttacker) {
    baseReward += 3;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0027" || name?.includes("莫亞")) && isAttacker) {
    const grave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
    const orcsInGrave = grave.filter(c => c && c.type === "unit" && (c.faction === "獸人" || c.id?.includes("ORC")));
    if (orcsInGrave.length > 0) {
      if (isPlayer) {
        const choices = [
          { text: "✨ 獲得 +2★ 額外獎勵", value: "stars" },
          { text: "💀 從墓地回收一個獸人單位至手牌", value: "recycle" }
        ];
        const chosen = await showXLWChoiceModal("死靈法師獸人 莫亞 效果", "選擇戰鬥成功效果：", choices);
        if (chosen === "recycle") {
          const orcChoices = orcsInGrave.map((c, i) => ({ text: `${c.name} (${c.id})`, value: i }));
          const chosenOrcIdx = await showXLWChoiceModal("選擇墓地獸人", "請選擇一個獸人回收至手牌：", orcChoices);
          if (chosenOrcIdx !== null && chosenOrcIdx !== undefined) {
            const targetOrc = orcsInGrave[chosenOrcIdx];
            window.xlwAddGraveyardCardToHand(targetOrc, true);
            logBattle(`✨ 死靈法師獸人 莫亞 效果：將墓地中的【${targetOrc.name}】回收至手牌。`);
          } else {
            baseReward += 2;
            hasRewardEffect = true;
          }
        } else {
          baseReward += 2;
          hasRewardEffect = true;
        }
      } else {
        if (Math.random() < 0.5) {
          baseReward += 2;
          hasRewardEffect = true;
        } else {
          const targetOrc = orcsInGrave[Math.floor(Math.random() * orcsInGrave.length)];
          window.xlwAddGraveyardCardToHand(targetOrc, false);
          logBattle(`✨ 對手 死靈法師獸人 莫亞 效果：將墓地中的【${targetOrc.name}】回收至對手手牌。`);
        }
      }
    } else {
      baseReward += 2;
      hasRewardEffect = true;
    }
  }
  if ((cid === "R-ORC-0028" || cid === "R-ORC-0038" || cid === "R-ORC-0041" || name?.includes("激動獸人") || name?.includes("初心獸人") || name?.includes("士氣獸人")) && isAttacker) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0055" || name?.includes("戰勝初心獸人")) && isAttacker) {
    baseReward += 2;
    hasRewardEffect = true;
  }
  if ((cid === "SR-ORC-0021" || cid === "SSR-ORC-0021" || name?.includes("洛克塔")) && isAttacker) {
    const oppAtkVal = oppUnit.card && oppUnit.card.attack !== "盾" ? parseInt(oppUnit.card.attack) || 0 : 0;
    baseReward += oppAtkVal;
    hasRewardEffect = true;
  }
  if (cid === "SR-ORC-0062" || name?.includes("艾勒粉") || name?.includes("戰爭巨象")) {
    const orcEquipCount = (unit.equipments || []).filter(eqName => {
      return ["帽", "菜刀", "狼牙棒", "弓", "牛排", "斧", "戰錘", "盾牌", "面具"].some(x => eqName.includes(x));
    }).length;
    const xVal = orcEquipCount * 2;
    if (xVal > 0) {
      baseReward += xVal;
      hasRewardEffect = true;
    }
  }
  if (unit.equipments && unit.equipments.some(eq => eq.includes("戰錘"))) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if (isAttacker && ((isPlayer && window.XLW_playerOrcAwardActiveUntil >= turn) || (!isPlayer && window.XLW_enemyOrcAwardActiveUntil >= turn))) {
    baseReward += 1;
    hasRewardEffect = true;
  }
  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    safe_replace("applyCombatSuccessReward triggers", target_success_rewards, replacement_success_rewards)

    # 13.2. Add other combat triggers: R-ORC-0059 (懸賞獸人) passive and R-ORC-0024 self-destruction in resolveUnitCombat
    target_boar_check = """    const isWildBoar = attackerCard.id === "R-NMS-0062" || attackerCard.id === "R-NMS-0062-2" || attackerCard.name?.includes("野豬");
    if (isWildBoar) {"""

    replacement_boar_check = """    const isWildBoar = attackerCard.id === "R-NMS-0062" || attackerCard.id === "R-NMS-0062-2" || attackerCard.name?.includes("野豬");
    if (isWildBoar) {
      logBattle(`✨ 野豬 效果：進攻戰鬥成功，野豬一同送入墓地破壞！`);
      await destroyUnit(attZone, attIdx, successOwner, false, true);
    }
    const isBombOrc = attackerCard.id === "R-ORC-0024" || attackerCard.name?.includes("爆破獸人");
    if (isBombOrc) {
      logBattle(`✨ 爆破獸人 效果：戰鬥成功，自爆破壞！`);
      await destroyUnit(attZone, attIdx, successOwner, false, true);
    }
    // 懸賞獸人 (R-ORC-0059) 被動
    const hasBountyOrc = ["player_front", "player_back", "enemy_front", "enemy_back"].some(z => {
      const isPlayer = z.startsWith("player_");
      const matchOwner = isPlayer ? "player" : "enemy";
      if (matchOwner !== successOwner) return false;
      return field[z].some((u, i) => u && u.card && (u.card.id === "R-ORC-0059" || u.card.name?.includes("懸賞獸人")) && !window.isUnitSilenced(u, z, i));
    });
    if (hasBountyOrc) {
      const extraDeck = successOwner === "player" ? window.XLW_playerExtraDeck : (window.XLW_enemyExtraDeck || []);
      const targetIdx = extraDeck.findIndex(c => c && (c.id === "R-ORC-0058" || c.name?.includes("懸賞令")));
      if (targetIdx >= 0) {
        const bountyCard = extraDeck.splice(targetIdx, 1)[0];
        if (successOwner === "player") {
          hand.push(bountyCard);
          logBattle(`✨ 懸賞獸人 被動效果：由於獸人戰鬥成功，從額外區將【懸賞令】加入手牌！`);
        } else {
          if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
          window.XLW_ENEMY.hand.push(bountyCard);
          logBattle(`✨ 對手 懸賞獸人 被動效果：由於對手獸人戰鬥成功，從其額外區將【懸賞令】加入手牌！`);
        }
        render();
      }
    }
    if (false) {"""

    safe_replace("Orc combat triggers", target_boar_check, replacement_boar_check)

    # 14. getUnitAtk modifiers
    target_atk_mods = """// 3. 禁衛軍獸人 (SSR-ORC-0057) 被攻擊時 +2 攻擊力
  if (c.id === "SSR-ORC-0057" || c.name?.includes("禁衛軍獸人")) {"""

    replacement_atk_mods = """// R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }
  // SR-ORC-0062 戰爭巨象 艾勒粉
  if (c.id === "SR-ORC-0062" || c.name?.includes("艾勒粉") || c.name?.includes("戰爭巨象")) {
    const orcEquipCount = (unit.equipments || []).filter(eqName => {
      return ["帽", "菜刀", "狼牙棒", "弓", "牛排", "斧", "戰錘", "盾牌", "面具"].some(x => eqName.includes(x));
    }).length;
    baseAtk += orcEquipCount * 2;
  }
  // ORC-0002 背刺獸人
  if ((c.id === "ORC-0002" || c.name?.includes("背刺獸人")) && unit.attacking && unit.target) {
    const defUnit = field[unit.target.zone][unit.target.idx];
    if (defUnit && defUnit.tapped) {
      baseAtk += 3;
    }
  }
  // 有打有嘉獎! (ORC-0020) Buff
  const sideIsPlayer = zone && zone.startsWith("player_");
  if (c.faction === "獸人" || c.id?.includes("ORC")) {
    if ((sideIsPlayer && window.XLW_playerOrcAwardActiveUntil >= turn) || (!sideIsPlayer && window.XLW_enemyOrcAwardActiveUntil >= turn)) {
      baseAtk += 1;
    }
  }

  // 3. 禁衛軍獸人 (SSR-ORC-0057) 被攻擊時 +2 攻擊力
  if (c.id === "SSR-ORC-0057" || c.name?.includes("禁衛軍獸人")) {"""

    safe_replace("getUnitAtk modifiers", target_atk_mods, replacement_atk_mods)

    # 15. isUnitIndestructible check
    target_indestructible = """// 最後的早餐 (R-ART-0030) 永久戰鬥破壞抗性
  if ((c.id === "R-ART-0030" || c.name?.includes("最後的早餐")) && isCombatDestruction) return true;"""

    replacement_indestructible = """// 女法師獸人 艾娜 (SR-ORC-0022)：使我方場上原始攻擊力 <=2 的獸人單位不會被破壞
  if (c.faction === "獸人" || c.id?.includes("ORC")) {
    const rawAtk = c.attack !== "盾" ? parseInt(c.attack) || 0 : 0;
    if (rawAtk <= 2 && zone) {
      const isPlayer = zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      const hasAina = [sidePrefix + "front", sidePrefix + "back"].some(z => {
        return field[z].some((u, i) => {
          return u && u.card && (u.card.id === "SR-ORC-0022" || u.card.name?.includes("艾娜")) && !window.isUnitSilenced(u, z, i);
        });
      });
      if (hasAina) return true;
    }
  }

  // 最後的早餐 (R-ART-0030) 永久戰鬥破壞抗性
  if ((c.id === "R-ART-0030" || c.name?.includes("最後的早餐")) && isCombatDestruction) return true;"""

    safe_replace("isUnitIndestructible", target_indestructible, replacement_indestructible)

    # 16. Graveyard modal onclick
    target_grave_click = """    cardEl.onmouseover = () => showModal(card);
    listContainer.appendChild(cardEl);"""

    replacement_grave_click = """    cardEl.onmouseover = () => showModal(card);
    cardEl.onclick = async () => {
      if (phase === "召喚階段" && graveList === graveyard && playerBonusScore > 0) {
        if (card.id === "R-ORC-0038" || card.name?.includes("初心獸人")) {
          const confirm = await showXLWConfirm("初心獸人 效果發動", "是否消耗 1 點我方額外獎勵，將墓地中的【初心獸人】回收至手牌？");
          if (confirm) {
            playerBonusScore -= 1;
            const idx = graveyard.indexOf(card);
            if (idx >= 0) graveyard.splice(idx, 1);
            hand.push(card);
            logBattle("✨ 初心獸人 效果：消耗 1 點獎勵分，將墓地中的【初心獸人】回收至手牌！");
            render();
            overlay.remove();
          }
        } else if (card.id === "R-ORC-0055" || card.name?.includes("戰勝初心獸人")) {
          const emptySlots = window.xlwGetEmptyPlayerSlots();
          if (emptySlots.length > 0) {
            const confirm = await showXLWConfirm("戰勝初心獸人 效果發動", "是否消耗 1 點我方額外獎勵，將墓地中的【戰勝初心獸人】特殊召喚至場上？");
            if (confirm) {
              playerBonusScore -= 1;
              const idx = graveyard.indexOf(card);
              if (idx >= 0) graveyard.splice(idx, 1);
              await window.xlwSpecialSummonUnit(card, true);
              logBattle("✨ 戰勝初心獸人 效果：消耗 1 點獎勵分，將墓地中的【戰勝初心獸人】特殊召喚至場上！");
              render();
              overlay.remove();
            }
          } else {
            setStatus("場上無空格，無法特殊召喚戰勝初心獸人！");
          }
        }
      }
    };
    listContainer.appendChild(cardEl);"""

    safe_replace("Graveyard modal click", target_grave_click, replacement_grave_click)

    # 17. AI main phase turn-start triggers
    target_ai_main = """    // AI 召喚階段發動魔法卡
    await aiPlayMagicCardsSummonPhase();"""

    replacement_ai_main = """    // AI 永鬥神 奈祖爾 (SR-ORC-0026) 效果發動
    const aiNezhuls = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "SR-ORC-0026" || u.card.id === "SSR-ORC-0026" || u.card.name?.includes("奈祖爾"))) {
          if (!window.isUnitSilenced(u, z, i) && u.nezhulUsedTurn !== turn) {
            aiNezhuls.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    }
    for (const nz of aiNezhuls) {
      const tappedOrcs = [];
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u.tapped && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
            tappedOrcs.push(u);
          }
        });
      }
      if (tappedOrcs.length > 0) {
        const target = tappedOrcs[0];
        target.tapped = false;
        nz.unit.nezhulUsedTurn = turn;
        logBattle(`✨ 對手 永鬥神 奈祖爾 效果：使對手場上的【${target.card.name}】轉正！`);
        window.xlwTriggerOrcUntapSynergy(false);
        render();
      }
    }

    // AI 初心獸人 & 戰勝初心獸人 墓地效果
    if (enemyBonusScore > 0) {
      let aiGrave = window.XLW_ENEMY.grave || [];
      // 1. 戰勝初心獸人
      let index = aiGrave.findIndex(c => c && (c.id === "R-ORC-0055" || c.name?.includes("戰勝初心獸人")));
      const emptySlots = window.xlwGetEmptyEnemySlots();
      if (index >= 0 && emptySlots.length > 0) {
        const card = aiGrave.splice(index, 1)[0];
        enemyBonusScore -= 1;
        await window.xlwSpecialSummonUnit(card, false);
        logBattle("✨ 對手 戰勝初心獸人 效果：消耗對手 1 點獎勵分，將墓地中的【戰勝初心獸人】特殊召喚至場上！");
        render();
      }
      // 2. 初心獸人
      index = aiGrave.findIndex(c => c && (c.id === "R-ORC-0038" || c.name?.includes("初心獸人")));
      if (index >= 0) {
        const card = aiGrave.splice(index, 1)[0];
        enemyBonusScore -= 1;
        if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
        window.XLW_ENEMY.hand.push(card);
        logBattle("✨ 對手 初心獸人 效果：消耗對手 1 點獎勵分，將墓地中的【初心獸人】回收至手牌！");
        render();
      }
    }

    // AI 召喚階段發動魔法卡
    await aiPlayMagicCardsSummonPhase();"""

    safe_replace("AI main phase turn-start triggers", target_ai_main, replacement_ai_main)

    # 18. Player active skill clicks
    target_player_active = """            // (a-1) 如月車站 R-VLG-0018 (主動封存效果)
            if (obj.card.id === "R-VLG-0018" || obj.card.name?.includes("如月車站")) {"""

    replacement_player_active = """            // (o-1) 永鬥神 奈祖爾 (主要階段限一次，可使我方 1 獸人單位轉正)
            if (obj.card.id === "SR-ORC-0026" || obj.card.id === "SSR-ORC-0026" || obj.card.name?.includes("奈祖爾")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.nezhulUsedTurn === turn) {
                setStatus("永鬥神 奈祖爾 的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              const tappedOrcs = [];
              for (const z of ["player_front", "player_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u.tapped && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
                    tappedOrcs.push({ zone: z, idx: i, unit: u });
                  }
                });
              }
              if (tappedOrcs.length === 0) {
                setStatus("我方場上沒有被橫置的獸人單位可以轉正！");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmUse = await showXLWConfirm("永鬥神 奈祖爾 效果發動", "是否選擇一個我方被橫置的獸人單位轉正？");
              if (confirmUse) {
                const choices = tappedOrcs.map((u, i) => ({ text: `${u.zone.includes("front") ? "前排" : "後排"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                const chosenIdx = await showXLWChoiceModal("選擇轉正單位", "請選擇一個我方獸人：", choices);
                if (chosenIdx !== null && chosenIdx !== undefined) {
                  const target = tappedOrcs[chosenIdx];
                  target.unit.tapped = false;
                  obj.nezhulUsedTurn = turn;
                  logBattle(`✨ 永鬥神 奈祖爾 效果：使我方【${target.unit.card.name}】轉正！`);
                  window.xlwTriggerOrcUntapSynergy(true);
                  render();
                  if (isMultiplayer) {
                    sendFullGameStateToOpponent();
                  }
                }
              }
              return;
            }

            // (a-1) 如月車站 R-VLG-0018 (主動封存效果)
            if (obj.card.id === "R-VLG-0018" || obj.card.name?.includes("如月車站")) {"""

    safe_replace("Player active skill clicks", target_player_active, replacement_player_active)

    # 19.1. Reset temporary flags and active taunt in xlwResolveEndPhaseEffects
    target_end_phase = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {"""
    
    replacement_end_phase = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  await window.xlwTriggerMaskTaunt(isPlayerSide);
  window.XLW_orcAuntTriggeredThisTurn = false;
  window.XLW_orcCheatFairActive = false;
  window.XLW_enemyOrcCheatFairActive = false;"""

    safe_replace("End phase triggers", target_end_phase, replacement_end_phase)

    # 19.2. Spell Counter Chain 怒吼 (R-ORC-0036) negation results
    target_chain_negation = """if (isCountered) {
    if (S.owner === "me") {
      if (S.wasExiledByBomb) {"""

    replacement_chain_negation = """if (isCountered) {
    if (S.owner === "me") {
      if (S.wasRoared) {
        hand.push(S.card);
        window.XLW_playerCannotUseCardIdThisTurn = S.card.id;
        logBattle(`我方的魔法卡 ${S.card.name} 被對手【怒吼】無效並退回手牌！我方本回合不得再次使用該卡。`);
      } else if (S.wasExiledByBomb) {"""

    safe_replace("Chain negation player side", target_chain_negation, replacement_chain_negation)

    target_chain_negation_opp = """} else {
      if (S.wasExiledByBomb) {"""

    replacement_chain_negation_opp = """} else {
      if (S.wasRoared) {
        if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
        window.XLW_ENEMY.hand.push(S.card);
        window.XLW_enemyCannotUseCardIdThisTurn = S.card.id;
        logBattle(`對手的魔法卡 ${S.card.name} 被我方【怒吼】無效並退回其手牌！對手本回合不得再次使用該卡。`);
      } else if (S.wasExiledByBomb) {"""

    safe_replace("Chain negation opponent side", target_chain_negation_opp, replacement_chain_negation_opp)

    # 19.4. Add wasRoared flag resolution in resolveLocalSpellChain loop
    target_chain_roar_flag = """      if (counteringCard && targetCard) {
        const isTargetUnit = targetCard.type === "unit" || (targetCard.name && targetCard.name.includes("\\u9b54\\u6cd5\\u70b8\\u5f48\\u5ba2")) || targetCard.id === "NEU-0025";"""

    replacement_chain_roar_flag = """      if (counteringCard && targetCard) {
        const isRoar = counteringCard.name?.includes("怒吼") || counteringCard.id === "R-ORC-0036";
        if (isRoar) {
          spellChainStack[i - 1].wasRoared = true;
          resolved[i - 1] = false;
        }
        const isTargetUnit = targetCard.type === "unit" || (targetCard.name && targetCard.name.includes("\\u9b54\\u6cd5\\u70b8\\u5f48\\u5ba2")) || targetCard.id === "NEU-0025";"""

    safe_replace("wasRoared flag check", target_chain_roar_flag, replacement_chain_roar_flag)

    # 19.5. Add 怒吼 (R-ORC-0036) to promptNextChainAction filter
    target_prompt_roar = """    const counterCards = isLastItemUnit ? [] : hand.filter(c => {
      if (!c) return false;
      const name = c.name || "";
      const cid = c.id || "";
      return name.includes("魔法反制") ||"""

    replacement_prompt_roar = """    const lastItemCard = lastItem ? lastItem.card : null;
    const lastItemMana = lastItemCard ? Number(lastItemCard.mana || 0) : 0;
    const counterCards = isLastItemUnit ? [] : hand.filter(c => {
      if (!c) return false;
      const name = c.name || "";
      const cid = c.id || "";
      if (name.includes("怒吼") || cid === "R-ORC-0036") {
        return lastItemCard && lastItemCard.type === "magic" && lastItemMana >= 1;
      }
      return name.includes("魔法反制") ||"""

    safe_replace("怒吼 added to promptNextChainAction filter", target_prompt_roar, replacement_prompt_roar)

    # 19.6. Add 怒吼 (R-ORC-0036) to aiRespondToSpellChain counter card finding
    target_ai_roar = """  const counterCard = aiHand.find(c => {
    if (!c) return false;
    const name = c.name || "";
    const cid = c.id || "";
    return name.includes("魔法反制") ||"""

    replacement_ai_roar = """  const counterCard = aiHand.find(c => {
    if (!c) return false;
    const name = c.name || "";
    const cid = c.id || "";
    if (name.includes("怒吼") || cid === "R-ORC-0036") {
      return lastItem.card && lastItem.card.type === "magic" && Number(lastItem.card.mana || 0) >= 1;
    }
    return name.includes("魔法反制") ||"""

    safe_replace("怒吼 added to aiRespondToSpellChain counter card finding", target_ai_roar, replacement_ai_roar)

    # 19.7. Add 怒吼 (R-ORC-0036) usage block in castSpell
    target_cast_spell_top = """async function castSpell(handIndex) {
  try {
    xlwSanitizeGoatCardTypes();"""

    replacement_cast_spell_top = """async function castSpell(handIndex) {
  try {
    xlwSanitizeGoatCardTypes();
    const card = hand[handIndex];
    if (card && window.XLW_playerCannotUseCardIdThisTurn === card.id) {
      setStatus("受到【怒吼】效果限制，本回合我方不得再次使用該魔法卡！");
      return;
    }"""

    safe_replace("怒吼 player check in castSpell", target_cast_spell_top, replacement_cast_spell_top)

    # 19.8. Backup/Restore screamed/roared card in aiPlayMagicCardsSummonPhase
    target_ai_magic_summon = """async function aiPlayMagicCardsSummonPhase() {
  if (isMultiplayer) return;"""

    replacement_ai_magic_summon = """async function aiPlayMagicCardsSummonPhase() {
  if (isMultiplayer) return;
  
  let roaredCardBackup = null;
  let roaredCardIdx = -1;
  if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
    roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
    if (roaredCardIdx >= 0) {
      roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
    }
  }"""

    safe_replace("怒吼 AI check in aiPlayMagicCardsSummonPhase start", target_ai_magic_summon, replacement_ai_magic_summon)

    target_ai_magic_summon_end = """        logBattle(`✨ 對手 AI 從手牌發動了【酒醉挑釁】！強制將我方單位【${targetUnit.card.name}】移動至其酒客【${randSlot.drinkerName}】前方的空格（我方前排第 ${randSlot.idx + 1} 格）！`);
        render();
        await sleep(800);
      });
    }
  }
}"""

    replacement_ai_magic_summon_end = """        logBattle(`✨ 對手 AI 從手牌發動了【酒醉挑釁】！強制將我方單位【${targetUnit.card.name}】移動至其酒客【${randSlot.drinkerName}】前方的空格（我方前排第 ${randSlot.idx + 1} 格）！`);
        render();
        await sleep(800);
      });
    }
  }
  if (roaredCardBackup !== null && window.XLW_ENEMY.hand) {
    window.XLW_ENEMY.hand.splice(roaredCardIdx, 0, roaredCardBackup);
  }
}"""

    safe_replace("怒吼 AI check in aiPlayMagicCardsSummonPhase end", target_ai_magic_summon_end, replacement_ai_magic_summon_end)

    # 19.8b. Backup/Restore screamed/roared card in aiPlayMagicCardsDefensePhase
    target_ai_magic_defense = """async function aiPlayMagicCardsDefensePhase(lane, defender, defZone, defIdx, attacker, attZone) {
  if (isMultiplayer) return;"""

    replacement_ai_magic_defense = """async function aiPlayMagicCardsDefensePhase(lane, defender, defZone, defIdx, attacker, attZone) {
  if (isMultiplayer) return;
  
  let roaredCardBackup = null;
  let roaredCardIdx = -1;
  if (window.XLW_enemyCannotUseCardIdThisTurn && window.XLW_ENEMY.hand) {
    roaredCardIdx = window.XLW_ENEMY.hand.findIndex(c => c && c.id === window.XLW_enemyCannotUseCardIdThisTurn);
    if (roaredCardIdx >= 0) {
      roaredCardBackup = window.XLW_ENEMY.hand.splice(roaredCardIdx, 1)[0];
    }
  }"""

    safe_replace("怒吼 AI check in aiPlayMagicCardsDefensePhase start", target_ai_magic_defense, replacement_ai_magic_defense)

    target_ai_magic_defense_end = """          logBattle(`✨ 對手進行戰術佈陣：將弱小/高分脆皮單位【${frontUnit.card.name}】移動至後排以避免被攻擊！`);
          render();
          await sleep(800);
        }
      }
    }
  }
}"""

    replacement_ai_magic_defense_end = """          logBattle(`✨ 對手進行戰術佈陣：將弱小/高分脆皮單位【${frontUnit.card.name}】移動至後排以避免被攻擊！`);
          render();
          await sleep(800);
        }
      }
    }
  }
  if (roaredCardBackup !== null && window.XLW_ENEMY.hand) {
    window.XLW_ENEMY.hand.splice(roaredCardIdx, 0, roaredCardBackup);
  }
}"""

    safe_replace("怒吼 AI check in aiPlayMagicCardsDefensePhase end", target_ai_magic_defense_end, replacement_ai_magic_defense_end)

    # 19.9. Clear temporary cannot use flags in end turn
    target_end_phase_clear = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  await window.xlwTriggerMaskTaunt(isPlayerSide);
  window.XLW_orcAuntTriggeredThisTurn = false;
  window.XLW_orcCheatFairActive = false;
  window.XLW_enemyOrcCheatFairActive = false;"""

    replacement_end_phase_clear = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  await window.xlwTriggerMaskTaunt(isPlayerSide);
  window.XLW_orcAuntTriggeredThisTurn = false;
  window.XLW_orcCheatFairActive = false;
  window.XLW_enemyOrcCheatFairActive = false;
  window.XLW_playerCannotUseCardIdThisTurn = null;
  window.XLW_enemyCannotUseCardIdThisTurn = null;"""

    safe_replace("Cannot use flags cleared in end turn", target_end_phase_clear, replacement_end_phase_clear)

    # 19.10. Add 永鬥神 奈祖爾 combat shield in resolveUnitCombat
    target_combat_shield = """if (attackerShouldDie && isUnitIndestructible(attacker, attZone, attIdx, true)) {"""

    replacement_combat_shield = """// 永鬥神 奈祖爾 combat shield (attacker side)
  if (attackerShouldDie && attacker && attacker.card && (attacker.card.id === "SR-ORC-0026" || attacker.card.id === "SSR-ORC-0026" || attacker.card.name?.includes("奈祖爾")) && !window.isUnitSilenced(attacker, attZone, attIdx)) {
    const isPlayer = attZone.startsWith("player_");
    const bonusScore = isPlayer ? playerBonusScore : enemyBonusScore;
    if (bonusScore > 0) {
      let confirmShield = true;
      if (isPlayer) {
        confirmShield = await showXLWConfirm("永鬥神 奈祖爾 效果發動", "偵測到永鬥神將被破壞，是否消耗 1 點獎勵分使其免於破壞？");
      }
      if (confirmShield) {
        if (isPlayer) {
          playerBonusScore -= 1;
        } else {
          enemyBonusScore -= 1;
        }
        attackerShouldDie = false;
        logBattle(`✨ 永鬥神 奈祖爾 效果：消耗 1 點獎勵分，免除本次戰鬥破壞！`);
        renderScore();
      }
    }
  }
  // 永鬥神 奈祖爾 combat shield (defender side)
  if (defenderShouldDie && defender && defender.card && (defender.card.id === "SR-ORC-0026" || defender.card.id === "SSR-ORC-0026" || defender.card.name?.includes("奈祖爾")) && !window.isUnitSilenced(defender, defZone, defIdx)) {
    const isPlayer = defZone.startsWith("player_");
    const bonusScore = isPlayer ? playerBonusScore : enemyBonusScore;
    if (bonusScore > 0) {
      let confirmShield = true;
      if (isPlayer) {
        confirmShield = await showXLWConfirm("永鬥神 奈祖爾 效果發動", "偵測到永鬥神將被破壞，是否消耗 1 點獎勵分使其免於破壞？");
      }
      if (confirmShield) {
        if (isPlayer) {
          playerBonusScore -= 1;
        } else {
          enemyBonusScore -= 1;
        }
        defenderShouldDie = false;
        logBattle(`✨ 永鬥神 奈祖爾 效果：消耗 1 點獎勵分，免除本次戰鬥破壞！`);
        renderScore();
      }
    }
  }

  if (attackerShouldDie && isUnitIndestructible(attacker, attZone, attIdx, true)) {"""

    safe_replace("永鬥神 奈祖爾 combat shield", target_combat_shield, replacement_combat_shield)

    # 19.11. Add 替身忍法 target triggers
    # Player manual target:
    target_player_manual_target = """  attacker.attacking = true;
  attacker.target = { zone: finalZone, idx: finalIdx };"""
    
    replacement_player_manual_target = """  attacker.attacking = true;
  attacker.target = { zone: finalZone, idx: finalIdx };
  await window.xlwTriggerSubsituteNinja(finalZone, finalIdx);"""

    safe_replace("替身忍法 player manual target trigger", target_player_manual_target, replacement_player_manual_target)

    # AI auto target:
    target_ai_auto_target = """        enemyAttacker.attacking = true;
        enemyAttacker.target = { zone: finalZone, idx: finalIdx };"""
    
    replacement_ai_auto_target = """        enemyAttacker.attacking = true;
        enemyAttacker.target = { zone: finalZone, idx: finalIdx };
        await window.xlwTriggerSubsituteNinja(finalZone, finalIdx);"""

    safe_replace("替身忍法 AI auto target trigger", target_ai_auto_target, replacement_ai_auto_target)

    # Save the modified code back to static/game_v8.js
    open(filepath, "w", encoding="utf-8").write(code)
    print("All Phase 2 changes written successfully.")

if __name__ == '__main__':
    main()
