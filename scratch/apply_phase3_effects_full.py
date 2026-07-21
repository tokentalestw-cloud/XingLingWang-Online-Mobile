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

    # 1. triggerSneakAttackSuccessEffects (Player Side)
    target_player_sneak = """async function triggerSneakAttackSuccessEffects(card) {
  if (!card) return;
  
  // 1. 從此開始記錄偷襲成功次數
  window.XLW_turnSneakCount = (window.XLW_turnSneakCount || 0) + 1;
  logBattle(`🥷 偷襲成功！本回合累計偷襲成功次數：${window.XLW_turnSneakCount} 次。`);"""

    replacement_player_sneak = """async function triggerSneakAttackSuccessEffects(card) {
  if (!card) return;
  
  // 1. 從此開始記錄偷襲成功次數
  window.XLW_turnSneakCount = (window.XLW_turnSneakCount || 0) + 1;
  logBattle(`🥷 偷襲成功！本回合累計偷襲成功次數：${window.XLW_turnSneakCount} 次。`);

  // (a-彩虹) 彩虹幻象喵 (R-CAT-0030)
  if (card.id !== "R-CAT-0030" && !card.name?.includes("彩虹幻象喵")) {
    const rainbowIdx = hand.findIndex(c => c && (c.id === "R-CAT-0030" || c.name?.includes("彩虹幻象喵")));
    if (rainbowIdx >= 0) {
      const confirmUse = await showXLWConfirm("彩虹幻象喵 效果發動", "偵測到我方單位偷襲成功！是否棄置手牌中的【彩虹幻象喵】，使我方所有進攻單位獲得 +1 攻擊力？");
      if (confirmUse) {
        const rainbowCard = hand.splice(rainbowIdx, 1)[0];
        graveyard.push(rainbowCard);
        window.XLW_rainbowCatAtkBuffActive = true;
        logBattle("✨ 彩虹幻象喵 效果：棄置此卡，使我方所有進攻單位獲得 +1 攻擊力！");
        render();
      }
    }
  }

  // (a-干擾) 訊號干擾喵 (R-CAT-0031)
  if (card.id === "R-CAT-0031" || card.name?.includes("訊號干擾喵")) {
    const oppHand = window.XLW_ENEMY.hand || [];
    const oppDeck = window.XLW_ENEMY.deck || [];
    const validCards = oppHand.filter(c => c !== null);
    if (validCards.length > 0) {
      const targetCard = validCards[Math.floor(Math.random() * validCards.length)];
      const hIdx = oppHand.indexOf(targetCard);
      if (hIdx >= 0) oppHand.splice(hIdx, 1);
      oppDeck.push(targetCard);
      shuffle(oppDeck);
      const drawn = oppDeck.pop() || null;
      oppHand.push(drawn);
      logBattle(`✨ 訊號干擾喵 效果：使對手隨機將一張手牌【${targetCard.name}】洗回牌庫，並抽了 1 張牌！`);
      render();
    }
  }

  // (a-惡夢) 惡夢9命喵 (R-CAT-0035)
  if (card.id !== "R-CAT-0035" && !card.name?.includes("惡夢9命喵")) {
    const count = window.XLW_turnSneakCount || 0;
    if (count >= 3) {
      const nineIdx = graveyard.findIndex(c => c && (c.id === "R-CAT-0035" || c.name?.includes("惡夢9命喵")));
      const emptySlots = window.xlwGetEmptyPlayerSlots();
      if (nineIdx >= 0 && emptySlots.length > 0) {
        const nineCard = graveyard.splice(nineIdx, 1)[0];
        await window.xlwSpecialSummonUnit(nineCard, true);
        logBattle("✨ 惡夢9命喵 效果：本回合偷襲成功達到 3 次，從墓地特殊召喚【惡夢9命喵】！");
        render();
      }
    }
  }"""

    safe_replace("Player triggerSneakAttackSuccessEffects", target_player_sneak, replacement_player_sneak)

    # 2. triggerEnemySneakAttackSuccessEffects (Enemy Side)
    target_enemy_sneak = """async function triggerEnemySneakAttackSuccessEffects(card) {
  if (!card) return;

  // 對手偷襲成功時也記錄回合偷襲次數
  window.XLW_turnSneakCount = (window.XLW_turnSneakCount || 0) + 1;"""

    replacement_enemy_sneak = """async function triggerEnemySneakAttackSuccessEffects(card) {
  if (!card) return;

  // 對手偷襲成功時也記錄回合偷襲次數
  window.XLW_turnSneakCount = (window.XLW_turnSneakCount || 0) + 1;
  logBattle(`🥷 對手 偷襲成功！本回合累計偷襲成功次數：${window.XLW_turnSneakCount} 次。`);

  // (a-彩虹) 彩虹幻象喵 (R-CAT-0030)
  if (card.id !== "R-CAT-0030" && !card.name?.includes("彩虹幻象喵")) {
    const enemyHand = window.XLW_ENEMY.hand || [];
    const rainbowIdx = enemyHand.findIndex(c => c && (c.id === "R-CAT-0030" || c.name?.includes("彩虹幻象喵")));
    if (rainbowIdx >= 0 && Math.random() < 0.6) {
      const rainbowCard = enemyHand.splice(rainbowIdx, 1)[0];
      window.XLW_ENEMY.grave.push(rainbowCard);
      window.XLW_enemyRainbowCatAtkBuffActive = true;
      logBattle("✨ 對手 彩虹幻象喵 效果：對手棄置此卡，使對手所有進攻單位獲得 +1 攻擊力！");
      render();
    }
  }

  // (a-干擾) 訊號干擾喵 (R-CAT-0031)
  if (card.id === "R-CAT-0031" || card.name?.includes("訊號干擾喵")) {
    const oppHand = hand || [];
    const oppDeck = deck || [];
    const validCards = oppHand.filter(c => c !== null);
    if (validCards.length > 0) {
      const targetCard = validCards[Math.floor(Math.random() * validCards.length)];
      const hIdx = oppHand.indexOf(targetCard);
      if (hIdx >= 0) oppHand.splice(hIdx, 1);
      oppDeck.push(targetCard);
      shuffle(oppDeck);
      const drawn = oppDeck.pop() || null;
      oppHand.push(drawn);
      logBattle(`✨ 對手 訊號干擾喵 效果：使我方隨機將一張手牌【${targetCard.name}】洗回牌庫，並抽了 1 張牌！`);
      render();
    }
  }

  // (a-惡夢) 惡夢9命喵 (R-CAT-0035)
  if (card.id !== "R-CAT-0035" && !card.name?.includes("惡夢9命喵")) {
    const count = window.XLW_turnSneakCount || 0;
    if (count >= 3) {
      const enemyGrave = window.XLW_ENEMY.grave || [];
      const nineIdx = enemyGrave.findIndex(c => c && (c.id === "R-CAT-0035" || c.name?.includes("惡夢9命喵")));
      const emptySlots = window.xlwGetEmptyEnemySlots();
      if (nineIdx >= 0 && emptySlots.length > 0) {
        const nineCard = enemyGrave.splice(nineIdx, 1)[0];
        await window.xlwSpecialSummonUnit(nineCard, false);
        logBattle("✨ 對手 惡夢9命喵 效果：本回合對手偷襲成功達到 3 次，從墓地特殊召喚【惡夢9命喵】！");
        render();
      }
    }
  }"""

    safe_replace("Enemy triggerEnemySneakAttackSuccessEffects", target_enemy_sneak, replacement_enemy_sneak)

    # 3. getUnitAtk Modifiers for Rainbow Cat and Aku's Hammer
    target_atk_mods = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }"""

    replacement_atk_mods = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }
  // R-ORC-0033 阿庫瑪的戰錘
  if (unit.equipments && unit.equipments.some(eq => eq.includes("戰錘") || eq.includes("阿庫瑪的戰錘"))) {
    baseAtk += 1;
  }
  // 彩虹幻象喵 (R-CAT-0030) Buff
  if (unit.attacking) {
    const sideIsPlayer = zone && zone.startsWith("player_");
    if (sideIsPlayer && window.XLW_rainbowCatAtkBuffActive) {
      baseAtk += 1;
    } else if (!sideIsPlayer && window.XLW_enemyRainbowCatAtkBuffActive) {
      baseAtk += 1;
    }
  }"""

    safe_replace("getUnitAtk Modifiers (Rainbow / Hammer)", target_atk_mods, replacement_atk_mods)

    # 4. castSpell register Hammer, Shield, Ax
    target_cast_equip = """card.name?.includes("符咒帽") || card.name?.includes("菜刀") || card.name?.includes("狼牙棒") || card.name?.includes("弓箭") || card.name?.includes("戰斧牛排") || card.name?.includes("迴旋飛斧")) {"""

    replacement_cast_equip = """card.name?.includes("符咒帽") || card.name?.includes("菜刀") || card.name?.includes("狼牙棒") || card.name?.includes("弓箭") || card.name?.includes("戰斧牛排") || card.name?.includes("迴旋飛斧") || card.name?.includes("戰錘") || card.name?.includes("盾牌") || card.name?.includes("戰斧") || card.name?.includes("牛排")) {"""

    safe_replace("castSpell register Equipments", target_cast_equip, replacement_cast_equip)

    # 5. performSummonToSlot Equipments check
    target_perform_equip = """            const isOrc = obj.card?.faction === "獸人" || obj.card?.race === "獸人" || obj.card?.id?.includes("ORC") || obj.card?.id?.includes("0RC") || obj.card?.id?.includes("ROC");
            const isShield = window.XLW_equipSpellCard && window.XLW_equipSpellCard.name === "法術保護-護盾";"""

    replacement_perform_equip = """            const isOrc = obj.card?.faction === "獸人" || obj.card?.race === "獸人" || obj.card?.id?.includes("ORC") || obj.card?.id?.includes("0RC") || obj.card?.id?.includes("ROC");
            const isShield = window.XLW_equipSpellCard && (window.XLW_equipSpellCard.name === "法術保護-護盾" || window.XLW_equipSpellCard.name?.includes("盾牌") || window.XLW_equipSpellCard.name?.includes("戰錘"));"""

    safe_replace("performSummonToSlot Equipments check", target_perform_equip, replacement_perform_equip)

    # 6. xlw_isShieldUnit checker for Block equipment
    target_shield_check = """const atkVal = String(c.attack ?? c.atk ?? c.power ?? "").trim();"""
    
    replacement_shield_check = """if (unit.equipments && unit.equipments.some(eq => eq.includes("盾牌"))) {
    return true;
  }
  const atkVal = String(c.attack ?? c.atk ?? c.power ?? "").trim();"""

    safe_replace("xlw_isShieldUnit checker for Block equipment", target_shield_check, replacement_shield_check)

    # 7. performSummonToSlot Immediate Summons (魔拳喵喵, 喵店店長, 獸人小妹 莎莎)
    target_summon_imm = """      // C-ORC-0012 寶寶獸人
      if (card.id === "C-ORC-0012" || card.id === "R-ORC-0012" || card.id === "SSR-ORC-0012" || card.name?.includes("寶寶獸人")) {"""

    replacement_summon_imm = """      // R-CAT-0042 / SSR-CAT-0042 魔拳喵喵
      if (card.id === "R-CAT-0042" || card.id === "SSR-CAT-0042" || card.name?.includes("魔拳喵喵")) {
        const isPlayer = zone.startsWith("player_");
        const sidePrefix = isPlayer ? "player_" : "enemy_";
        const otherCats = [];
        [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
          field[z].forEach((u, i) => {
            if (u && u !== field[zone][idx] && u.card && (u.card.faction === "喵喵賊" || u.card.deck === "喵喵賊" || u.card.id?.includes("CAT"))) {
              otherCats.push({ zone: z, idx: i, unit: u });
            }
          });
        });
        if (otherCats.length > 0) {
          if (isPlayer) {
            const choices = otherCats.map((item, cIdx) => ({
              text: `${item.unit.card.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`,
              value: cIdx
            }));
            const chosen = await showXLWChoiceModal("魔拳喵喵 效果發動", "請選擇另一個要獲得魔法抗性的喵喵賊單位：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = otherCats[chosen];
              target.unit.magicImmuneUntilTurn = turn + 2;
              target.unit.equipments = target.unit.equipments || [];
              target.unit.equipments.push("魔拳魔法抗性");
              logBattle(`✨ 魔拳喵喵 效果：我方【${target.unit.card.name}】獲得魔法抗性直到下個回合結束！`);
              render();
            }
          } else {
            const target = otherCats[0];
            target.unit.magicImmuneUntilTurn = turn + 2;
            target.unit.equipments = target.unit.equipments || [];
            target.unit.equipments.push("魔拳魔法抗性");
            logBattle(`✨ 對手 魔拳喵喵 效果：對手【${target.unit.card.name}】獲得魔法抗性直到下個回合結束！`);
            render();
          }
        }
      }

      // R-CAT-0051 喵店店長
      if (card.id === "R-CAT-0051" || card.name?.includes("喵店店長")) {
        const isPlayer = zone.startsWith("player_");
        const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
        const eligibleOpponentCats = myHand.filter(c => {
          if (!c) return false;
          const isCat = c.faction === "喵喵賊" || c.deck === "喵喵賊" || c.id?.includes("CAT");
          const canOpponent = c.effect_text?.includes("敵方場上") || c.effect_text?.includes("敵方後牌") || c.id === "R-CAT-0037" || c.id === "R-CAT-0043" || c.name?.includes("喵抓板") || c.name?.includes("喵喵球") || c.name?.includes("殭屍女") || c.name?.includes("背後靈") || c.name?.includes("人臉魚");
          return isCat && canOpponent;
        });
        const emptyOpponentSlots = isPlayer ? window.xlwGetEmptyEnemySlots() : window.xlwGetEmptyPlayerSlots();
        if (eligibleOpponentCats.length > 0 && emptyOpponentSlots.length > 0) {
          if (isPlayer) {
            const confirm = await showXLWConfirm("喵店店長 效果發動", "是否發動【喵店店長】效果，從手牌選擇一隻可召喚於敵方場上的喵喵賊單位額外特殊召喚？");
            if (confirm) {
              const choices = eligibleOpponentCats.map((c, i) => ({ text: `${c.name}`, value: i }));
              const chosenIdx = await showXLWChoiceModal("選擇額外召喚的喵喵卡", "請選擇一隻卡牌：", choices);
              if (chosenIdx !== null && chosenIdx !== undefined) {
                const chosenCard = eligibleOpponentCats[chosenIdx];
                const hIdx = hand.indexOf(chosenCard);
                if (hIdx >= 0) hand.splice(hIdx, 1);
                
                selectedHandForSummon = hand.indexOf(chosenCard);
                window.XLW_bypassNormalSummonLimit = true;
                setStatus(`【喵店店長 特召】請點選對手場上一個空格特殊召喚【${chosenCard.name}】！`);
                render();
                await new Promise(r => { window.XLW_summonPlacementResolve = r; });
              }
            }
          } else {
            const chosenCard = eligibleOpponentCats[0];
            const hIdx = myHand.indexOf(chosenCard);
            if (hIdx >= 0) myHand.splice(hIdx, 1);
            await window.xlwSpecialSummonUnit(chosenCard, false);
            logBattle(`✨ 對手 喵店店長 效果：在對手場上額外特殊召喚了【${chosenCard.name}】！`);
            render();
          }
        }
      }

      // R-ORC-0037 獸人小妹 莎莎
      if (card.id === "R-ORC-0037" || card.name?.includes("莎莎")) {
        const isPlayer = zone.startsWith("player_");
        const sidePrefix = isPlayer ? "player_" : "enemy_";
        const otherOrcs = [];
        [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
          field[z].forEach((u, i) => {
            if (u && u !== field[zone][idx] && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
              otherOrcs.push({ zone: z, idx: i, unit: u });
            }
          });
        });
        if (otherOrcs.length > 0) {
          if (isPlayer) {
            const choices = otherOrcs.map((item, cIdx) => ({
              text: `${item.unit.card.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`,
              value: cIdx
            }));
            const chosen = await showXLWChoiceModal("獸人小妹 莎莎 效果發動", "請選擇另一個我方獸人單位郵寄予 +2 攻擊力：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = otherOrcs[chosen];
              target.unit.atkModifier = (target.unit.atkModifier || 0) + 2;
              target.unit.equipments = target.unit.equipments || [];
              target.unit.equipments.push("莎莎(+2)");
              logBattle(`✨ 獸人小妹 莎莎 效果：使我方【${target.unit.card.name}】獲得 +2 攻擊力直到對手下回合主要階段開始！`);
              render();
            }
          } else {
            const target = otherOrcs[0];
            target.unit.atkModifier = (target.unit.atkModifier || 0) + 2;
            target.unit.equipments = target.unit.equipments || [];
            target.unit.equipments.push("莎莎(+2)");
            logBattle(`✨ 對手 獸人小妹 莎莎 效果：使對手【${target.unit.card.name}】獲得 +2 攻擊力直到我方下回合主要階段開始！`);
            render();
          }
        }
      }

      // C-ORC-0012 寶寶獸人
      if (card.id === "C-ORC-0012" || card.id === "R-ORC-0012" || card.id === "SSR-ORC-0012" || card.name?.includes("寶寶獸人")) {"""

    safe_replace("performSummonToSlot Immediate Summons", target_summon_imm, replacement_summon_imm)

    # 8. xlwResolveTurnStartEffects Sasha Buff Expire Check
    target_turn_start = """window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
  const prefix = isPlayerSide ? "player_" : "enemy_";"""

    replacement_turn_start = """window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
  const prefix = isPlayerSide ? "player_" : "enemy_";

  // Clean up Sasha's buff on the opponent of the active player
  const oppPrefix = isPlayerSide ? "enemy_" : "player_";
  ["front", "back"].forEach(r => {
    field[oppPrefix + r].forEach(u => {
      if (u && u.equipments && u.equipments.includes("莎莎(+2)")) {
        u.equipments = u.equipments.filter(e => e !== "莎莎(+2)");
        u.atkModifier = Math.max(0, (u.atkModifier || 0) - 2);
        logBattle(`✨ 獸人小妹 莎莎 效果結束：【${u.card.name}】攻擊力回復。`);
      }
    });
  });"""

    safe_replace("xlwResolveTurnStartEffects Sasha Buff Expire Check", target_turn_start, replacement_turn_start)

    # 9. changeActionPhase Lingsao Movement Trigger (Player Side)
    target_tactical_lingsao = """  if (phase === "戰術佈陣") {
    // 恐怖小丑 (R-VLG-0048) 效果"""

    replacement_tactical_lingsao = """  if (phase === "戰術佈陣") {
    // 靈騷獸人 (R-ORC-0030) 效果
    const hasLingsao = ["player_front", "player_back"].some(z => {
      return field[z].some((u, i) => u && u.card && (u.card.id === "R-ORC-0030" || u.card.name?.includes("靈騷獸人")) && !window.isUnitSilenced(u, z, i));
    });
    if (hasLingsao && !window.XLW_lingsaoTriggeredThisTurn) {
      const orcUnits = [];
      for (const z of ["player_front", "player_back"]) {
        field[z].forEach((u, i) => {
          if (u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
            orcUnits.push({ zone: z, idx: i, unit: u });
          }
        });
      }
      const emptySlots = window.xlwGetEmptyPlayerSlots();
      if (orcUnits.length > 0 && emptySlots.length > 0) {
        const confirmMove = await showXLWConfirm("靈騷獸人 效果發動", "是否發動【靈騷獸人】效果，在戰術階段開始時額外移動一個我方獸人單位？");
        if (confirmMove) {
          window.XLW_lingsaoTriggeredThisTurn = true;
          const choices = orcUnits.map((u, i) => ({ text: `${u.unit.card.name} (${u.zone.includes("front") ? "前排" : "後排"}${u.idx + 1})`, value: i }));
          const chosenIdx = await showXLWChoiceModal("選擇移動的獸人", "選擇一個獸人單位：", choices);
          if (chosenIdx !== null && chosenIdx !== undefined) {
            const target = orcUnits[chosenIdx];
            const slotChoices = emptySlots.map((s, i) => ({ text: `${s.zone.includes("front") ? "前排" : "後排"}${s.idx + 1}`, value: i }));
            const chosenSlotIdx = await showXLWChoiceModal("選擇目的格子", "選擇一個空格：", slotChoices);
            if (chosenSlotIdx !== null && chosenSlotIdx !== undefined) {
              const dest = emptySlots[chosenSlotIdx];
              field[dest.zone][dest.idx] = target.unit;
              field[target.zone][target.idx] = null;
              logBattle(`✨ 靈騷獸人 效果：將【${target.unit.card.name}】移動到 ${dest.zone.includes("front") ? "前排" : "後排"}${dest.idx + 1}！`);
              render();
              if (isMultiplayer) {
                sendFullGameStateToOpponent();
              }
            }
          }
        }
      }
    }

    // 恐怖小丑 (R-VLG-0048) 效果"""

    safe_replace("changeActionPhase Lingsao Movement Trigger (Player Side)", target_tactical_lingsao, replacement_tactical_lingsao)

    # 10. runEnemyTurn Lingsao Movement Trigger (AI/Enemy Side)
    target_ai_lingsao = """      // AI 恐怖小丑 (R-VLG-0048) 效果發動
      const enemyGrave = window.XLW_ENEMY.grave || [];"""

    replacement_ai_lingsao = """      // AI 靈騷獸人 (R-ORC-0030) 效果發動
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

    # 11. xlwResolveEndPhaseEffects Flag Resets
    target_end_phase_resets = """  window.XLW_orcAuntTriggeredThisTurn = false;
  window.XLW_orcCheatFairActive = false;
  window.XLW_enemyOrcCheatFairActive = false;"""

    replacement_end_phase_resets = """  window.XLW_orcAuntTriggeredThisTurn = false;
  window.XLW_orcCheatFairActive = false;
  window.XLW_enemyOrcCheatFairActive = false;
  window.XLW_lingsaoTriggeredThisTurn = false;
  window.XLW_enemyLingsaoTriggeredThisTurn = false;
  window.XLW_rainbowCatAtkBuffActive = false;
  window.XLW_enemyRainbowCatAtkBuffActive = false;
  window.XLW_turnSneakCount = 0;"""

    safe_replace("xlwResolveEndPhaseEffects Flag Resets", target_end_phase_resets, replacement_end_phase_resets)

    # 12. destroyUnit checks (作弊獸人, 阿姨獸人)
    target_destroy_checks = """async function destroyUnit(zone, idx, owner, shouldExile, isCombatDestruction = false) {
  const unit = field[zone][idx];
  if (!unit) return;"""

    replacement_destroy_checks = """async function destroyUnit(zone, idx, owner, shouldExile, isCombatDestruction = false) {
  const unit = field[zone][idx];
  if (!unit) return;

  // C-ORC-0060 作弊獸人 戰鬥失敗額外分數
  if (isCombatDestruction && unit.card && (unit.card.id === "C-ORC-0060" || unit.card.name?.includes("作弊獸人")) && !window.isUnitSilenced(unit, zone, idx)) {
    const isPlayer = zone.startsWith("player_");
    if (isPlayer) {
      playerBonusScore += 3;
      logBattle("✨ 作弊獸人 效果發動：戰鬥失敗，我方額外獎勵 +3★！");
    } else {
      enemyBonusScore += 3;
      logBattle("✨ 對手 作弊獸人 效果發動：戰鬥失敗，對手額外獎勵 +3★！");
    }
    renderScore();
  }

  // R-ORC-0023 阿姨獸人 敵方小旅人被擊破效果
  if (isCombatDestruction && unit.card && (unit.card.id === "TOKEN_TRAVELER" || unit.card.name?.includes("小旅人"))) {
    const isPlayerTraveler = zone.startsWith("player_");
    const checkSidePrefix = isPlayerTraveler ? "enemy_" : "player_";
    const hasAuntOrc = [checkSidePrefix + "front", checkSidePrefix + "back"].some(z => {
      return field[z].some((u, i) => u && u.card && (u.card.id === "R-ORC-0023" || u.card.name?.includes("阿姨獸人")) && !window.isUnitSilenced(u, z, i));
    });
    if (hasAuntOrc) {
      if (isPlayerTraveler) {
        enemyBonusScore += 1;
        logBattle("✨ 對手 阿姨獸人 效果發動：我方小旅人被戰鬥破壞，對手額外獎勵 +1★！");
      } else {
        playerBonusScore += 1;
        logBattle("✨ 我方 阿姨獸人 效果發動：對手小旅人被戰鬥破壞，我方額外獎勵 +1★！");
      }
      renderScore();
    }
  }"""

    safe_replace("destroyUnit checks (作弊獸人, 阿姨獸人)", target_destroy_checks, replacement_destroy_checks)

    # 13. applyCombatSuccessReward neighbor shield check
    target_shield_reward = """  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    replacement_shield_reward = """  // ORC-0011 盾牌獸人 & R-ORC-0050 盾牌獸人的盾牌 鄰近戰鬥成功效果
  let uZone = null, uIdx = -1;
  for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
    const idx = field[z].indexOf(unit);
    if (idx >= 0) {
      uZone = z;
      uIdx = idx;
      break;
    }
  }
  if (uZone) {
    const neighbors = [uIdx - 1, uIdx + 1];
    for (const nIdx of neighbors) {
      if (nIdx >= 0 && nIdx < 5) {
        const neighborUnit = field[uZone][nIdx];
        if (neighborUnit && neighborUnit.card) {
          const isShieldOrc = neighborUnit.card.id === "ORC-0011" || neighborUnit.card.name?.includes("盾牌獸人");
          const hasShieldEquip = neighborUnit.equipments && neighborUnit.equipments.some(eq => eq.includes("盾牌獸人的盾牌") || eq.includes("盾牌"));
          if ((isShieldOrc || hasShieldEquip) && !window.isUnitSilenced(neighborUnit, uZone, nIdx)) {
            baseReward += 1;
            hasRewardEffect = true;
            logBattle(`✨ 鄰近【${neighborUnit.card.name}】的效果：【${unit.card.name}】戰鬥成功，額外獎勵 +1★！`);
          }
        }
      }
    }
  }

  // R-ORC-0042-繪畫 / R-ORC-0042 背背獸人 寄合加分
  if (unit.hasBeibeiOrc || (unit.equipments && unit.equipments.includes("背背獸人"))) {
    baseReward += 2;
    hasRewardEffect = true;
    logBattle(`✨ 背背獸人 合體效果：我方額外獎勵 +2★！`);
  }

  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    safe_replace("applyCombatSuccessReward neighbor shield check", target_shield_reward, replacement_shield_reward)

    # 14. resolveUnitCombat Flat Tie-Breaker
    target_tie_breaker = """  // 基礎戰鬥數值對決 (相同攻擊力時攻擊方獲勝，防守方被破壞)
  if (atkPower >= defPower) {
    defenderShouldDie = true;
    attackerShouldDie = false;
  } else {
    attackerShouldDie = true;
    defenderShouldDie = false;
  }"""

    replacement_tie_breaker = """  // 基礎戰鬥數值對決 (相同攻擊力時攻擊方獲勝，防守方被破壞)
  if (atkPower > defPower) {
    defenderShouldDie = true;
    attackerShouldDie = false;
  } else if (defPower > atkPower) {
    attackerShouldDie = true;
    defenderShouldDie = false;
  } else {
    // 平手 (atkPower === defPower)
    // 天下第一獸人作弊大會 (ORC-0019) 效果發動：平手視為我方獲勝！
    let playerCheated = false;
    let enemyCheated = false;
    
    if (defender.card && (defender.card.faction === "獸人" || defender.card.id?.includes("ORC")) && !window.isUnitSilenced(defender, defZone, defIdx)) {
      if (defZone.startsWith("player_") && window.XLW_orcCheatFairActive) {
        playerCheated = true;
      } else if (defZone.startsWith("enemy_") && window.XLW_enemyOrcCheatFairActive) {
        enemyCheated = true;
      }
    }
    if (attacker.card && (attacker.card.faction === "獸人" || attacker.card.id?.includes("ORC")) && !window.isUnitSilenced(attacker, attZone, attIdx)) {
      if (attZone.startsWith("player_") && window.XLW_orcCheatFairActive) {
        playerCheated = true;
      } else if (attZone.startsWith("enemy_") && window.XLW_enemyOrcCheatFairActive) {
        enemyCheated = true;
      }
    }

    if (playerCheated && !enemyCheated) {
      if (attZone.startsWith("player_")) {
        defenderShouldDie = true;
        attackerShouldDie = false;
      } else {
        defenderShouldDie = false;
        attackerShouldDie = true;
      }
      logBattle("✨ 天下第一獸人作弊大會 效果：攻擊力平手改為我方戰鬥成功！");
    } else if (enemyCheated && !playerCheated) {
      if (attZone.startsWith("enemy_")) {
        defenderShouldDie = true;
        attackerShouldDie = false;
      } else {
        defenderShouldDie = false;
        attackerShouldDie = true;
      }
      logBattle("✨ 對手 天下第一獸人作弊大會 效果：攻擊力平手改為對手戰鬥成功！");
    } else {
      // 預設規則：攻擊方獲勝，防守方被破壞
      defenderShouldDie = true;
      attackerShouldDie = false;
    }
  }"""

    safe_replace("resolveUnitCombat Flat Tie-Breaker", target_tie_breaker, replacement_tie_breaker)

    # 15. Player Active Skill Click for Beibei Orc Combination
    target_active_skills = """            // (o-1) 永鬥神 奈祖爾 (主要階段限一次，可使我方 1 獸人單位轉正)"""

    replacement_active_skills = """            // (o-beibei) 背背獸人 R-ORC-0042 / R-ORC-0042-繪畫 合體寄生主動技能
            if (obj.card.id === "R-ORC-0042" || obj.card.id === "R-ORC-0042-繪畫" || obj.card.name?.includes("背背獸人")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.beibeiEffectUsedTurn === turn) {
                setStatus("背背獸人的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              
              const myOrcs = [];
              const sidePrefix = zone.startsWith("player_") ? "player_" : "enemy_";
              [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
                field[z].forEach((u, i) => {
                  if (u && u !== obj && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
                    myOrcs.push({ zone: z, idx: i, unit: u });
                  }
                });
              });
              if (myOrcs.length === 0) {
                setStatus("我方場上沒有其他獸人單位可以進行寄生合體！");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmCombine = await showXLWConfirm("背背獸人 合體效果", "是否發動【背背獸人】效果，對我方場上另一個獸人單位發動寄生合體？（合體後此單位將離場，宿主戰鬥成功獎勵 +2★）");
              if (confirmCombine) {
                const choices = myOrcs.map((u, i) => ({ text: `${u.zone.includes("front") ? "前排" : "後排"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                const chosenIdx = await showXLWChoiceModal("選擇合體宿主", "請選擇一個獸人宿主：", choices);
                if (chosenIdx !== null && chosenIdx !== undefined) {
                  const targetHost = myOrcs[chosenIdx];
                  targetHost.unit.equipments = targetHost.unit.equipments || [];
                  targetHost.unit.equipments.push("背背獸人");
                  targetHost.unit.hasBeibeiOrc = true;
                  field[zone][idx] = null;
                  logBattle(`✨ 背背獸人 效果：成功寄生合體至【${targetHost.unit.card.name}】！`);
                  render();
                  if (isMultiplayer) {
                    sendFullGameStateToOpponent();
                  }
                }
              }
              return;
            }

            // (o-1) 永鬥神 奈祖爾 (主要階段限一次，可使我方 1 獸人單位轉正)"""

    safe_replace("Player Active Skill Click for Beibei Orc Combination", target_active_skills, replacement_active_skills)

    # 15.2 AI Active Skill trigger for Beibei Orc in runEnemyTurn
    target_ai_turn_start = """    // AI 永鬥神 奈祖爾 (SR-ORC-0026) 效果發動"""

    replacement_ai_turn_start = """    // AI 背背獸人 (R-ORC-0042 / R-ORC-0042-繪畫) 效果發動
    const aiBeibeis = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "R-ORC-0042" || u.card.id === "R-ORC-0042-繪畫" || u.card.name?.includes("背背獸人"))) {
          if (!window.isUnitSilenced(u, z, i) && u.beibeiEffectUsedTurn !== turn) {
            aiBeibeis.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    }
    for (const bb of aiBeibeis) {
      const myOrcs = [];
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u !== bb.unit && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))) {
            myOrcs.push(u);
          }
        });
      }
      if (myOrcs.length > 0) {
        const host = myOrcs[0];
        host.equipments = host.equipments || [];
        host.equipments.push("背背獸人");
        host.hasBeibeiOrc = true;
        field[bb.zone][bb.idx] = null;
        logBattle(`✨ 對手 背背獸人 效果：寄生合體至對手【${host.card.name}】！`);
        render();
      }
    }

    // AI 永鬥神 奈祖爾 (SR-ORC-0026) 效果發動"""

    safe_replace("AI Active Skill trigger for Beibei Orc", target_ai_turn_start, replacement_ai_turn_start)

    # 16. castSpell add Cheat Fair spell activation
    target_cast_cheat_fair = """  } else if (card.name.includes("山羊術")) {"""

    replacement_cast_cheat_fair = """  } else if (card.id === "ORC-0019" || card.name.includes("天下第一獸人作弊大會")) {
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    
    await castSpellChain(spellCard, async () => {
      window.XLW_orcCheatFairActive = true;
      logBattle("✨ 我方發動了【天下第一獸人作弊大會】！本回合我方獸人單位攻擊力平手改為我方戰鬥成功！");
      render();
    });
  } else if (card.name.includes("山羊術")) {"""

    safe_replace("castSpell add Cheat Fair spell activation", target_cast_cheat_fair, replacement_cast_cheat_fair)

    # 17. AI cast Cheat Fair spell in aiPlayMagicCardsSummonPhase
    target_ai_cast_spell_top = """  // 大雷擊：當我方總分落後 10★ 或以上時，破壞玩家前排所有單位"""

    replacement_ai_cast_spell_top = """  // 天下第一獸人作弊大會 (ORC-0019)
  const cheatIdx = hand.findIndex(c => c && (c.id === "ORC-0019" || c.name?.includes("天下第一獸人作弊大會")));
  if (cheatIdx >= 0) {
    const myOrcsCount = ["enemy_front", "enemy_back"].reduce((sum, z) => sum + field[z].filter(u => u && u.card && (u.card.faction === "獸人" || u.card.id?.includes("ORC"))).length, 0);
    if (myOrcsCount >= 2) {
      const spellCard = hand.splice(cheatIdx, 1)[0];
      await xlwShowSpellActivationOverlay(spellCard, "enemy");
      await aiCastSpell(spellCard, async () => {
        window.XLW_enemyOrcCheatFairActive = true;
        logBattle("✨ 對手 AI 發動了【天下第一獸人作弊大會】！對手本回合平手視為戰鬥成功！");
        render();
      });
    }
  }

  // 大雷擊：當我方總分落後 10★ 或以上時，破壞玩家前排所有單位"""

    safe_replace("AI cast Cheat Fair spell", target_ai_cast_spell_top, replacement_ai_cast_spell_top)

    # Save the modified code back to static/game_v8.js
    open(filepath, "w", encoding="utf-8").write(code)
    print("All Phase 3 changes written successfully.")

if __name__ == '__main__':
    main()
