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

    # 1. Helpers section insertion
    target_helpers = """// ===== 喵喵賊偷襲系統變數 ====="""
    replacement_helpers = """// ===== 歡樂島系統變數與輔助函式 =====
window.XLW_tonghuluUsedThisTurn = false;
window.XLW_wanziUsedThisTurn = false;
window.XLW_enemyWanziUsedThisTurn = false;

window.isMahjongUnit = function(card) {
  if (!card) return false;
  const name = card.name || "";
  return name.includes("東大哥") || name.includes("南大姊") || name.includes("西小弟") || name.includes("北小妹") || name.includes("紅中哥") || name.includes("白板哥") || name.includes("發財哥") || name.includes("萬字大叔") || name.includes("防抓貓") || name.includes("詐胡牌") || card.id === "R-FMS-0031";
};

window.xlwCheckMahjongCombo = function(isPlayer, comboType) {
  const sidePrefix = isPlayer ? "player_" : "enemy_";
  const namesOnField = [];
  let zhaHuCount = 0;
  for (const r of ["front", "back"]) {
    field[sidePrefix + r].forEach(u => {
      if (u && u.card) {
        if (u.card.name?.includes("詐胡牌") || u.card.id === "R-FMS-0031") {
          zhaHuCount++;
        } else {
          namesOnField.push(u.card.name);
        }
      }
    });
  }
  
  if (comboType === "小四喜") {
    const required = ["東大哥", "北小妹", "西小弟", "南大姊"];
    let missing = 0;
    required.forEach(req => {
      const has = namesOnField.some(n => n && n.includes(req));
      if (!has) missing++;
    });
    return zhaHuCount >= missing;
  }
  
  if (comboType === "大三元") {
    const required = ["紅中哥", "白板哥", "發財哥"];
    let missing = 0;
    required.forEach(req => {
      const has = namesOnField.some(n => n && n.includes(req));
      if (!has) missing++;
    });
    return zhaHuCount >= missing;
  }
  
  return false;
};

window.xlwRevealCard = async function(card, isPlayer) {
  if (!card) return;
  logBattle(`✨ 展示卡牌：【${card.name}】（${isPlayer ? "我方" : "對手"}）`);
  
  let triggered = false;
  
  // R-FMS-0026 V領黑熊
  if (card.id === "R-FMS-0026" || card.name?.includes("V領黑熊")) {
    triggered = true;
    const oppSide = isPlayer ? "enemy" : "player";
    const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
    const targets = [];
    oppZones.forEach(z => {
      field[z].forEach((u, i) => {
        if (u && !isUnitEffectImmune(u, z, i)) {
          const uAtk = getUnitAtk(u, z, i);
          const cardAtk = card.attack ?? card.atk ?? card.power ?? 0;
          if (uAtk <= cardAtk) {
            targets.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    });
    if (targets.length > 0) {
      if (isPlayer) {
        const choices = targets.map((t, idx) => ({ text: `${t.zone.includes("front") ? "前排" : "後排"}${t.idx + 1} 的 ${t.unit.card.name}`, value: idx }));
        const chosen = await showXLWChoiceModal("V領黑熊 效果發動", "選擇一個要破壞的敵方單位：", choices);
        if (chosen !== null && chosen !== undefined) {
          const t = targets[chosen];
          logBattle(`✨ V領黑熊 效果：破壞對手場上的【${t.unit.card.name}】！`);
          await destroyUnit(t.zone, t.idx, oppSide, false);
          render();
        }
      } else {
        const t = targets[Math.floor(Math.random() * targets.length)];
        logBattle(`✨ 對手 V領黑熊 效果：破壞我方場上的【${t.unit.card.name}】！`);
        await destroyUnit(t.zone, t.idx, oppSide, false);
        render();
      }
    }
  }

  // R-FMS-0033 刈包
  if (card.id === "R-FMS-0033" || card.name?.includes("刈包")) {
    triggered = true;
    const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
    const eligibleGrave = myGrave.filter(c => {
      if (!c) return false;
      const isHappyIsland = c.faction === "歡樂島" || c.deck === "歡樂島" || c.id?.includes("FMS");
      const stars = c.stars ?? c.star ?? getCardTributeCost(c) ?? 0;
      return isHappyIsland && stars <= 3;
    });
    const emptySlots = isPlayer ? window.xlwGetEmptyPlayerSlots() : window.xlwGetEmptyEnemySlots();
    if (eligibleGrave.length > 0 && emptySlots.length > 0) {
      if (isPlayer) {
        const choices = eligibleGrave.map((c, i) => ({ text: `${c.name} (${c.id})`, value: i }));
        const chosen = await showXLWChoiceModal("刈包 效果發動", "選擇一個墓地中3星或以下的歡樂島單位特殊召喚：", choices);
        if (chosen !== null && chosen !== undefined) {
          const chosenCard = eligibleGrave[chosen];
          const gIdx = graveyard.indexOf(chosenCard);
          if (gIdx >= 0) graveyard.splice(gIdx, 1);
          await window.xlwSpecialSummonUnit(chosenCard, true);
          logBattle(`✨ 刈包 效果：從墓地特殊召喚了【${chosenCard.name}】！`);
          render();
        }
      } else {
        const chosenCard = eligibleGrave[0];
        const gIdx = myGrave.indexOf(chosenCard);
        if (gIdx >= 0) myGrave.splice(gIdx, 1);
        await window.xlwSpecialSummonUnit(chosenCard, false);
        logBattle(`✨ 對手 刈包 效果：從對手墓地特殊召喚了【${chosenCard.name}】！`);
        render();
      }
    }
  }

  // SR-FMS-0004 旺來酥
  if (card.id === "SR-FMS-0004" || card.name?.includes("旺來酥")) {
    triggered = true;
    if (isPlayer) {
      playerBonusScore += 2;
      logBattle("✨ 旺來酥 效果發動：我方額外分數 +2★！");
    } else {
      enemyBonusScore += 2;
      logBattle("✨ 對手 旺來酥 效果發動：對手額外分數 +2★！");
    }
    renderScore();
  }

  // SR-FMS-0025 綠繡眼 & SR-FMS-0028 高價櫻花鮭魚
  if (card.id === "SR-FMS-0025" || card.id === "SR-FMS-0025-泳裝" || card.id === "SR-FMS-0028" || card.name?.includes("綠繡眼") || card.name?.includes("櫻花鮭魚")) {
    triggered = true;
    const emptySlots = isPlayer ? window.xlwGetEmptyPlayerSlots() : window.xlwGetEmptyEnemySlots();
    if (emptySlots.length > 0) {
      const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
      const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
      const dIdx = myDeck.indexOf(card);
      if (dIdx >= 0) {
        myDeck.splice(dIdx, 1);
      } else {
        const hIdx = myHand.indexOf(card);
        if (hIdx >= 0) myHand.splice(hIdx, 1);
      }
      await window.xlwSpecialSummonUnit(card, isPlayer);
      logBattle(`✨ ${card.name} 效果：此卡被展示，特殊召喚至【${isPlayer ? "我方" : "對手"}】場上！`);
      render();
    }
  }

  // 女王石 SR-FMS-0033
  if (triggered) {
    const sidePrefix = isPlayer ? "player_" : "enemy_";
    const queenStoneSlots = [];
    [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "SR-FMS-0033" || u.card.name?.includes("女王石")) && !window.isUnitSilenced(u, z, i)) {
          queenStoneSlots.push({ zone: z, idx: i, unit: u });
        }
      });
    });
    for (const q of queenStoneSlots) {
      if (isPlayer) {
        playerBonusScore += 1;
        logBattle("✨ 女王石 效果發動：我方有卡牌因被展示而觸發效果，我方額外分數 +1★！");
      } else {
        enemyBonusScore += 1;
        logBattle("✨ 對手 女王石 效果發動：對手有卡牌因被展示而觸發效果，對手額外分數 +1★！");
      }
      renderScore();
      const success = await window.xlwSpecialSummonUnit(LITTLE_TRAVELER, isPlayer);
      if (!success) break;
    }
  }
};

window.xlwRevealTopCards = async function(count, isPlayer) {
  const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
  if (myDeck.length === 0) return [];
  
  let actualCount = count;
  const hasTonghulu = [isPlayer ? "player_front" : "enemy_front", isPlayer ? "player_back" : "enemy_back"].some(z => {
    return field[z].some((u, i) => u && u.card && (u.card.id === "R-FMS-0006" || u.card.id === "SSSR-FMS-0006" || u.card.name?.includes("糖葫蘆小童")) && !window.isUnitSilenced(u, z, i));
  });
  
  let tonghuluActive = false;
  if (hasTonghulu && !window.XLW_tonghuluUsedThisTurn) {
    tonghuluActive = true;
    actualCount += 1;
  }
  
  const cards = [];
  for (let i = 0; i < actualCount; i++) {
    if (myDeck.length > i) {
      cards.push(myDeck[myDeck.length - 1 - i]);
    }
  }
  
  if (cards.length === 0) return [];
  
  for (const c of cards) {
    await window.xlwRevealCard(c, isPlayer);
  }
  
  if (tonghuluActive && cards.length > 1) {
    window.XLW_tonghuluUsedThisTurn = true;
    if (isPlayer) {
      const choices = cards.map((c, i) => ({ text: `${c.name}`, value: i }));
      const chosen = await showXLWChoiceModal("糖葫蘆小童 效果發動", "選擇其中一張作為本次效果依據：", choices);
      if (chosen !== null && chosen !== undefined) {
        logBattle(`✨ 糖葫蘆小童 效果：選擇了【${cards[chosen].name}】作為效果依據。`);
        return [cards[chosen]];
      }
    } else {
      logBattle(`✨ 對手 糖葫蘆小童 效果：選擇了【${cards[0].name}】作為效果依據。`);
      return [cards[0]];
    }
  }
  
  return cards.slice(0, count);
};

// ===== 喵喵賊偷襲系統變數 ====="""

    safe_replace("Central Helpers & Variables", target_helpers, replacement_helpers)

    # 2. R-FMS-0001 (三寶) & R-FMS-0022 (萬字大叔) replacement in destroyUnit
    target_destroy_three_treasures = """async function destroyUnit(zone, idx, owner, shouldExile, isCombatDestruction = false) {
  const unit = field[zone][idx];
  if (!unit) return;"""

    replacement_destroy_three_treasures = """async function destroyUnit(zone, idx, owner, shouldExile, isCombatDestruction = false) {
  const unit = field[zone][idx];
  if (!unit) return;

  // R-FMS-0022 萬字大叔 代替破壞效果
  if (unit.card && window.isMahjongUnit(unit.card) && !unit.card.name?.includes("萬字大叔")) {
    const isPlayer = zone.startsWith("player_");
    const sidePrefix = isPlayer ? "player_" : "enemy_";
    const hasWanzi = [sidePrefix + "front", sidePrefix + "back"].some(z => {
      return field[z].some((u, i) => u && u.card && (u.card.id === "R-FMS-0022" || u.card.name?.includes("萬字大叔")) && !window.isUnitSilenced(u, z, i));
    });
    const wanziUsed = isPlayer ? window.XLW_wanziUsedThisTurn : window.XLW_enemyWanziUsedThisTurn;
    if (hasWanzi && !wanziUsed) {
      const otherMahjongs = [];
      [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
        field[z].forEach((u, i) => {
          if (u && u !== unit && u.card && window.isMahjongUnit(u.card)) {
            otherMahjongs.push({ zone: z, idx: i, name: u.card.name });
          }
        });
      });
      if (otherMahjongs.length > 0) {
        if (isPlayer) {
          const confirmSubstitute = await showXLWConfirm("萬字大叔 效果發動", `我方麻將單位【${unit.card.name}】即將被破壞，是否發動【萬字大叔】效果，選擇另一個我方麻將單位代替破壞？`);
          if (confirmSubstitute) {
            const choices = otherMahjongs.map((item, idx) => ({ text: `${item.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`, value: idx }));
            const chosen = await showXLWChoiceModal("選擇代替破壞的麻將", "請選擇代替破壞的單位：", choices);
            if (chosen !== null && chosen !== undefined) {
              const target = otherMahjongs[chosen];
              window.XLW_wanziUsedThisTurn = true;
              logBattle(`✨ 萬字大叔 效果：我方【${target.name}】代替【${unit.card.name}】被破壞！`);
              await destroyUnit(target.zone, target.idx, "player", false);
              return; // Skip original destruction!
            }
          }
        } else {
          // AI substitute
          const target = otherMahjongs[0];
          window.XLW_enemyWanziUsedThisTurn = true;
          logBattle(`✨ 對手 萬字大叔 效果：對手【${target.name}】代替【${unit.card.name}】被破壞！`);
          await destroyUnit(target.zone, target.idx, "enemy", false);
          return; // Skip original destruction!
        }
      }
    }
  }

  // R-FMS-0001 三寶 戰鬥被破壞效果
  if (isCombatDestruction && unit.card && (unit.card.id === "R-FMS-0001" || unit.card.name?.includes("三寶")) && !window.isUnitSilenced(unit, zone, idx)) {
    const isPlayer = zone.startsWith("player_");
    const oppPrefix = isPlayer ? "enemy_" : "player_";
    const oppOwner = isPlayer ? "enemy" : "player";
    let oppTargetZone = null, oppTargetIdx = -1;
    if (field[oppPrefix + "front"][idx]) {
      oppTargetZone = oppPrefix + "front";
      oppTargetIdx = idx;
    } else if (field[oppPrefix + "back"][idx]) {
      oppTargetZone = oppPrefix + "back";
      oppTargetIdx = idx;
    }
    if (oppTargetZone) {
      logBattle(`✨ 三寶 效果發動：前方敵方單位【${field[oppTargetZone][oppTargetIdx].card.name}】同歸於盡破壞！`);
      await destroyUnit(oppTargetZone, oppTargetIdx, oppOwner, false);
    }
  }"""

    safe_replace("destroyUnit hooks (三寶, 萬字大叔)", target_destroy_three_treasures, replacement_destroy_three_treasures)

    # 3. getUnitAtk check for 臭豆腐屍 (FMS-0005)
    target_shoudoufu_atk = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }"""

    replacement_shoudoufu_atk = """  // R-ORC-0007 鐵獸人
  if ((c.id === "R-ORC-0007" || c.name?.includes("鐵獸人")) && isBeingAttacked) {
    baseAtk += 2;
  }
  // R-FMS-0005 臭豆腐屍 正前方攻擊降低 2
  if (zone && idx !== undefined && idx >= 0) {
    const sidePrefix = zone.startsWith("player_") ? "player_" : "enemy_";
    const oppPrefix = zone.startsWith("player_") ? "enemy_" : "player_";
    let oppStinky = false;
    
    // Check direct opposite row
    const oppositeRow = zone.includes("front") ? "front" : "back";
    const oppUnit = field[oppPrefix + oppositeRow][idx];
    if (oppUnit && oppUnit.card && (oppUnit.card.id === "R-FMS-0005" || oppUnit.card.name?.includes("臭豆腐屍")) && !window.isUnitSilenced(oppUnit, oppPrefix + oppositeRow, idx)) {
      oppStinky = true;
    }
    
    if (oppStinky) {
      baseAtk = Math.max(0, baseAtk - 2);
    }
  }"""

    safe_replace("getUnitAtk check for 臭豆腐屍", target_shoudoufu_atk, replacement_shoudoufu_atk)

    # 4. Sun Cake (太陽餅 R-FMS-0003) check in castSpell
    target_suncake_cast = """async function castSpell(card, handIndex) {
  if (!card) return;"""

    replacement_suncake_cast = """async function castSpell(card, handIndex) {
  if (!card) return;

  // R-FMS-0003 太陽餅 場地限制
  const isFieldSpell = card.art_subtype === "場地" || card.magic_type === "場地" || card.name?.includes("場地") || card.name?.includes("世界") || card.name?.includes("電影院") || card.name?.includes("井") || card.name?.includes("鬼屋");
  if (isFieldSpell) {
    let hasSunCake = false;
    for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "R-FMS-0003" || u.card.name?.includes("太陽餅")) && !window.isUnitSilenced(u, z, i)) {
          hasSunCake = true;
        }
      });
    }
    if (hasSunCake) {
      setStatus("場上有太陽餅生效中，雙方不得使用場地魔法卡！");
      return;
    }
  }"""

    safe_replace("Sun Cake (太陽餅) check in castSpell", target_suncake_cast, replacement_suncake_cast)

    # 5. R-FMS-0012 東大哥 / R-FMS-0024 民熊鬼屋 / R-FMS-0029 尪仔標 at Turn Start
    target_turn_start_happy_island = """window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
  const prefix = isPlayerSide ? "player_" : "enemy_";"""

    replacement_turn_start_happy_island = """window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
  const prefix = isPlayerSide ? "player_" : "enemy_";

  // R-FMS-0012 東大哥 效果 (主要階段開始時手牌回牌庫頂)
  const hasEastBro = [prefix + "front", prefix + "back"].some(z => {
    return field[z].some((u, i) => u && u.card && (u.card.id === "R-FMS-0012" || u.card.name?.includes("東大哥")) && !window.isUnitSilenced(u, z, i));
  });
  if (hasEastBro) {
    const myHand = isPlayerSide ? hand : (window.XLW_ENEMY.hand || []);
    const myDeck = isPlayerSide ? deck : (window.XLW_ENEMY.deck || []);
    if (myHand.length > 0) {
      if (isPlayerSide) {
        const confirmEast = await showXLWConfirm("東大哥 效果發動", "是否發動【東大哥】效果，將一張手牌放回牌庫頂？");
        if (confirmEast) {
          const choices = myHand.map((c, i) => ({ text: `${c.name}`, value: i }));
          const chosen = await showXLWChoiceModal("選擇放回牌庫頂的手牌", "請選擇一張卡牌：", choices);
          if (chosen !== null && chosen !== undefined) {
            const cardToReturn = myHand.splice(chosen, 1)[0];
            myDeck.push(cardToReturn);
            logBattle(`✨ 東大哥 效果：將我方手牌【${cardToReturn.name}】放回牌庫頂！`);
            render();
          }
        }
      } else {
        // AI East Bro
        const cardToReturn = myHand.splice(0, 1)[0];
        myDeck.push(cardToReturn);
        logBattle(`✨ 對手 東大哥 效果：對手將手牌【${cardToReturn.name}】放回其牌庫頂！`);
        render();
      }
    }
  }

  // R-FMS-0024 民熊鬼屋 效果 (主要階段開始時展示牌庫頂重洗)
  const playerField = $("playerField");
  const enemyField = $("enemyField");
  const fCard = isPlayerSide ? (playerField?.dataset.card ? JSON.parse(playerField.dataset.card) : null) : (enemyField?.dataset.card ? JSON.parse(enemyField.dataset.card) : null);
  if (fCard && (fCard.id === "R-FMS-0024" || fCard.name?.includes("民熊鬼屋"))) {
    const myGrave = isPlayerSide ? graveyard : (window.XLW_ENEMY.grave || []);
    const unitGraveCount = myGrave.filter(c => c && c.type === "unit").length;
    const x = Math.min(3, unitGraveCount);
    if (x > 0) {
      if (isPlayerSide) {
        const confirmGhost = await showXLWConfirm("民熊鬼屋 效果發動", `是否發動【民熊鬼屋】效果，展示我方牌庫頂 ${x} 張牌並重新洗牌？`);
        if (confirmGhost) {
          await window.xlwRevealTopCards(x, true);
          const myDeck = isPlayerSide ? deck : (window.XLW_ENEMY.deck || []);
          shuffle(myDeck);
          logBattle("✨ 民熊鬼屋 效果：重洗我方牌庫！");
          render();
        }
      } else {
        // AI ghost house
        await window.xlwRevealTopCards(x, false);
        const myDeck = isPlayerSide ? deck : (window.XLW_ENEMY.deck || []);
        shuffle(myDeck);
        logBattle("✨ 對手 民熊鬼屋 效果：重洗對手牌庫！");
        render();
      }
    }
  }

  // R-FMS-0029 尪仔標 效果
  const hasDoll = [prefix + "front", prefix + "back"].some(z => {
    return field[z].some((u, i) => u && u.card && (u.card.id === "R-FMS-0029" || u.card.name?.includes("尪仔標")) && !window.isUnitSilenced(u, z, i));
  });
  if (hasDoll) {
    const myDeck = isPlayerSide ? deck : (window.XLW_ENEMY.deck || []);
    const oppDeck = isPlayerSide ? (window.XLW_ENEMY.deck || []) : deck;
    if (myDeck.length > 0 && oppDeck.length > 0) {
      const confirmDoll = isPlayerSide ? await showXLWConfirm("尪仔標 效果發動", "是否發動【尪仔標】效果展示雙方牌庫頂並進行對決？") : true;
      if (confirmDoll) {
        const myCard = myDeck[myDeck.length - 1];
        const oppCard = oppDeck[oppDeck.length - 1];
        await window.xlwRevealCard(myCard, isPlayerSide);
        await window.xlwRevealCard(oppCard, !isPlayerSide);
        
        if (myCard.type === "unit" && oppCard.type === "unit") {
          const myAtk = myCard.attack ?? myCard.atk ?? myCard.power ?? 0;
          const oppAtk = oppCard.attack ?? oppCard.atk ?? oppCard.power ?? 0;
          if (myAtk >= oppAtk) {
            const oppSide = isPlayerSide ? "enemy" : "player";
            const oppZones = isPlayerSide ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
            const targets = [];
            oppZones.forEach(z => {
              field[z].forEach((u, i) => {
                if (u && !isUnitEffectImmune(u, z, i)) targets.push({ zone: z, idx: i, unit: u });
              });
            });
            if (targets.length > 0) {
              if (isPlayerSide) {
                const choices = targets.map((t, idx) => ({ text: `${t.zone.includes("front") ? "前排" : "後排"}${t.idx + 1} 的 ${t.unit.card.name}`, value: idx }));
                const chosen = await showXLWChoiceModal("選擇變身小旅人的目標", "請選擇一個敵方單位：", choices);
                if (chosen !== null && chosen !== undefined) {
                  const t = targets[chosen];
                  t.unit.card = structuredClone(LITTLE_TRAVELER);
                  t.unit.equipments = [];
                  t.unit.atkModifier = 0;
                  logBattle(`✨ 尪仔標 效果：對手【${t.unit.card.name}】變身為【小旅人】！`);
                  render();
                }
              } else {
                // AI Doll transformation
                const t = targets[Math.floor(Math.random() * targets.length)];
                t.unit.card = structuredClone(LITTLE_TRAVELER);
                t.unit.equipments = [];
                t.unit.atkModifier = 0;
                logBattle(`✨ 對手 尪仔標 效果：我方【${t.unit.card.name}】變身為【小旅人】！`);
                render();
              }
            }
          }
        }
      }
    }
  }"""

    safe_replace("Turn Start Happy Island Triggers", target_turn_start_happy_island, replacement_turn_start_happy_island)

    # 6. xlwResolveEndPhaseEffects Flag Resets
    target_end_phase_happy = """  window.XLW_lingsaoTriggeredThisTurn = false;
  window.XLW_enemyLingsaoTriggeredThisTurn = false;
  window.XLW_rainbowCatAtkBuffActive = false;
  window.XLW_enemyRainbowCatAtkBuffActive = false;
  window.XLW_turnSneakCount = 0;"""

    replacement_end_phase_happy = """  window.XLW_lingsaoTriggeredThisTurn = false;
  window.XLW_enemyLingsaoTriggeredThisTurn = false;
  window.XLW_rainbowCatAtkBuffActive = false;
  window.XLW_enemyRainbowCatAtkBuffActive = false;
  window.XLW_turnSneakCount = 0;
  window.XLW_tonghuluUsedThisTurn = false;
  window.XLW_wanziUsedThisTurn = false;
  window.XLW_enemyWanziUsedThisTurn = false;"""

    safe_replace("xlwResolveEndPhaseEffects Flag Resets Happy Island", target_end_phase_happy, replacement_end_phase_happy)

    # 7. Pearl Milk Tea (珍珠ㄋㄟ茶) & 沒花鹿 in applyCombatSuccessReward
    target_pearl_success = """  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    replacement_pearl_success = """  // R-FMS-0002 珍珠ㄋㄟ茶 效果
  if ((cid === "R-FMS-0002" || cid === "R-FMS-0002-泳裝" || cid === "SSR-FMS-0002" || name?.includes("珍珠ㄋㄟ茶")) && !window.isUnitSilenced(unit)) {
    const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
    const eligibleHand = myHand.filter(c => c && (c.faction === "歡樂島" || c.deck === "歡樂島" || c.id?.includes("FMS")) && c.type === "unit");
    if (eligibleHand.length > 0) {
      if (isPlayer) {
        const confirmPearl = await showXLWConfirm("珍珠ㄋㄟ茶 效果發動", "是否展示手牌中一張歡樂島單位以破壞敵方一個攻擊力小於等於該卡的單位？");
        if (confirmPearl) {
          const choices = eligibleHand.map((c, i) => ({ text: `${c.name} (${c.id})`, value: i }));
          const chosen = await showXLWChoiceModal("選擇展示的手牌", "請選擇一張卡牌：", choices);
          if (chosen !== null && chosen !== undefined) {
            const chosenCard = eligibleHand[chosen];
            await window.xlwRevealCard(chosenCard, true);
            
            const cardAtk = chosenCard.attack ?? chosenCard.atk ?? chosenCard.power ?? 0;
            const oppSide = "enemy";
            const oppZones = ["enemy_front", "enemy_back"];
            const targets = [];
            oppZones.forEach(z => {
              field[z].forEach((u, i) => {
                if (u && !isUnitEffectImmune(u, z, i)) {
                  const uAtk = getUnitAtk(u, z, i);
                  if (uAtk <= cardAtk) {
                    targets.push({ zone: z, idx: i, unit: u });
                  }
                }
              });
            });
            if (targets.length > 0) {
              const targetChoices = targets.map((t, i) => ({ text: `${t.zone.includes("front") ? "前排" : "後排"}${t.idx + 1} 的 ${t.unit.card.name}`, value: i }));
              const targetChosen = await showXLWChoiceModal("選擇破壞目標", "請選擇要破壞的目標：", targetChoices);
              if (targetChosen !== null && targetChosen !== undefined) {
                const targetUnit = targets[targetChosen];
                logBattle(`✨ 珍珠ㄋㄟ茶 效果：破壞對手場上的【${targetUnit.unit.card.name}】！`);
                await destroyUnit(targetUnit.zone, targetUnit.idx, oppSide, false);
                render();
              }
            }
          }
        }
      } else {
        // AI Pearl Milk Tea
        const chosenCard = eligibleHand[0];
        await window.xlwRevealCard(chosenCard, false);
        const cardAtk = chosenCard.attack ?? chosenCard.atk ?? chosenCard.power ?? 0;
        const oppZones = ["player_front", "player_back"];
        const targets = [];
        oppZones.forEach(z => {
          field[z].forEach((u, i) => {
            if (u && !isUnitEffectImmune(u, z, i)) {
              const uAtk = getUnitAtk(u, z, i);
              if (uAtk <= cardAtk) {
                targets.push({ zone: z, idx: i, unit: u });
              }
            }
          });
        });
        if (targets.length > 0) {
          const targetUnit = targets[Math.floor(Math.random() * targets.length)];
          logBattle(`✨ 對手 珍珠ㄋㄟ茶 效果：破壞我方場上的【${targetUnit.unit.card.name}】！`);
          await destroyUnit(targetUnit.zone, targetUnit.idx, "player", false);
          render();
        }
      }
    }
  }

  // R-FMS-0027 沒花鹿 效果
  if ((cid === "R-FMS-0027" || name?.includes("沒花鹿")) && isAttacker && !window.isUnitSilenced(unit)) {
    const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
    if (myHand.length > 0) {
      if (isPlayer) {
        const confirmDeer = await showXLWConfirm("沒花鹿 效果發動", "是否展示手牌中一張卡牌？");
        if (confirmDeer) {
          const choices = myHand.map((c, i) => ({ text: `${c.name}`, value: i }));
          const chosen = await showXLWChoiceModal("選擇展示的手牌", "請選擇一張卡牌：", choices);
          if (chosen !== null && chosen !== undefined) {
            await window.xlwRevealCard(myHand[chosen], true);
          }
        }
      } else {
        // AI Deer
        await window.xlwRevealCard(myHand[0], false);
      }
    }
  }

  if ((cid === "R-ORC-0015" || name?.includes("獸人弓箭手")) && isAttacker) {"""

    safe_replace("Pearl Milk Tea & Deer triggers", target_pearl_success, replacement_pearl_success)

    # 8. High Tower (高塔101號) Play Eligibility check in canSummonCard
    target_tower_play = """function canSummonCard(card) {
  if (!card) return false;"""

    replacement_tower_play = """function canSummonCard(card) {
  if (!card) return false;

  // R-FMS-0030 / SSR-FMS-0030 高塔101號 限制
  if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
    const ok = window.xlwCheckMahjongCombo(true, "小四喜");
    if (!ok) {
      return false;
    }
  }"""

  # Note: AI also checks playerSummonLimit, we can block it in play logic too.
    safe_replace("High Tower play eligibility check", target_tower_play, replacement_tower_play)

    # 9. performSummonToSlot Immediate Summons (大腸包小腸, 麻將兄弟, 北小妹, 西小弟, 南大姊, 詐胡牌, 好大雞牌, 高塔101, 東北/西南季風, 麻祖)
    target_summon_happy = """      // R-CAT-0042 / SSR-CAT-0042 魔拳喵喵"""

    replacement_summon_happy = """      // R-FMS-0007 大腸包小腸
      if (card.id === "R-FMS-0007" || card.name?.includes("大腸包小腸")) {
        const isPlayer = zone.startsWith("player_");
        const rev = await window.xlwRevealTopCards(1, isPlayer);
        if (rev.length > 0 && rev[0].type === "unit") {
          const revAtk = rev[0].attack ?? rev[0].atk ?? rev[0].power ?? 0;
          const oppSide = isPlayer ? "enemy" : "player";
          const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
          const targets = [];
          oppZones.forEach(z => {
            field[z].forEach((u, i) => {
              if (u && !isUnitEffectImmune(u, z, i)) {
                const uAtk = getUnitAtk(u, z, i);
                if (uAtk <= revAtk) {
                  targets.push({ zone: z, idx: i, unit: u });
                }
              }
            });
          });
          if (targets.length > 0) {
            if (isPlayer) {
              const choices = targets.map((t, idx) => ({ text: `${t.zone.includes("front") ? "前排" : "後排"}${t.idx + 1} 的 ${t.unit.card.name}`, value: idx }));
              const chosen = await showXLWChoiceModal("大腸包小腸 綁架效果", "選擇一個要綁架的敵方單位：", choices);
              if (chosen !== null && chosen !== undefined) {
                const t = targets[chosen];
                await kidnapCard(t.zone, t.idx, zone, idx);
                render();
              }
            } else {
              const t = targets[Math.floor(Math.random() * targets.length)];
              await kidnapCard(t.zone, t.idx, zone, idx);
              render();
            }
          }
        }
      }

      // R-FMS-0009 / R-FMS-0010 / R-FMS-0011 紅中哥/白板哥/發財哥
      if (card.name?.includes("紅中哥") || card.name?.includes("白板哥") || card.name?.includes("發財哥")) {
        const isPlayer = zone.startsWith("player_");
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        if (myDeck.length > 0) {
          const rev = await window.xlwRevealTopCards(1, isPlayer);
          if (rev.length > 0) {
            const rName = rev[0].name || "";
            const isBrother = rName.includes("紅中哥") || rName.includes("白板哥") || rName.includes("發財哥");
            if (isBrother && rName !== card.name) {
              const emptySlots = isPlayer ? window.xlwGetEmptyPlayerSlots() : window.xlwGetEmptyEnemySlots();
              if (emptySlots.length > 0) {
                myDeck.pop(); // remove from top
                await window.xlwSpecialSummonUnit(rev[0], isPlayer);
                logBattle(`✨ 麻將兄弟連動：成功特殊召喚了【${rev[0].name}】！`);
                render();
              }
            }
          }
        }
      }

      // R-FMS-0013 北小妹
      if (card.id === "R-FMS-0013" || card.name?.includes("北小妹")) {
        const isPlayer = zone.startsWith("player_");
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        const mahjongs = myDeck.filter(c => c && window.isMahjongUnit(c));
        if (mahjongs.length > 0) {
          if (isPlayer) {
            const choices = mahjongs.map((c, i) => ({ text: `${c.name}`, value: i }));
            const chosen = await showXLWChoiceModal("北小妹 效果發動", "選擇一張要放回牌庫頂的麻將單位卡：", choices);
            if (chosen !== null && chosen !== undefined) {
              const targetCard = mahjongs[chosen];
              const dIdx = deck.indexOf(targetCard);
              if (dIdx >= 0) deck.splice(dIdx, 1);
              shuffle(deck);
              deck.push(targetCard);
              logBattle(`✨ 北小妹 效果：從牌庫尋找【${targetCard.name}】放回牌庫頂！`);
              render();
            }
          } else {
            const targetCard = mahjongs[0];
            const dIdx = myDeck.indexOf(targetCard);
            if (dIdx >= 0) myDeck.splice(dIdx, 1);
            shuffle(myDeck);
            myDeck.push(targetCard);
            logBattle(`✨ 對手 北小妹 效果：從對手牌庫尋找【${targetCard.name}】放回其牌庫頂！`);
            render();
          }
        }
      }

      // R-FMS-0014 西小弟
      if (card.id === "R-FMS-0014" || card.name?.includes("西小弟")) {
        const isPlayer = zone.startsWith("player_");
        const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        const islandUnits = myGrave.filter(c => c && (c.faction === "歡樂島" || c.deck === "歡樂島" || c.id?.includes("FMS")));
        if (islandUnits.length > 0) {
          if (isPlayer) {
            const choices = islandUnits.map((c, i) => ({ text: `${c.name}`, value: i }));
            const chosen = await showXLWChoiceModal("西小弟 效果發動", "選擇一張墓地中的歡樂島單位卡放回牌庫頂：", choices);
            if (chosen !== null && chosen !== undefined) {
              const targetCard = islandUnits[chosen];
              const gIdx = graveyard.indexOf(targetCard);
              if (gIdx >= 0) graveyard.splice(gIdx, 1);
              deck.push(targetCard);
              logBattle(`✨ 西小弟 效果：將墓地中的【${targetCard.name}】放回牌庫頂！`);
              render();
            }
          } else {
            const targetCard = islandUnits[0];
            const gIdx = myGrave.indexOf(targetCard);
            if (gIdx >= 0) myGrave.splice(gIdx, 1);
            myDeck.push(targetCard);
            logBattle(`✨ 對手 西小弟 效果：將對手墓地中的【${targetCard.name}】放回其牌庫頂！`);
            render();
          }
        }
      }

      // R-FMS-0015 南大姊
      if (card.id === "R-FMS-0015" || card.name?.includes("南大姊")) {
        const isPlayer = zone.startsWith("player_");
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
        if (myDeck.length > 0) {
          const rev = await window.xlwRevealTopCards(1, isPlayer);
          if (rev.length > 0) {
            const isMahjong = window.isMahjongUnit(rev[0]);
            const isHu = rev[0].id === "SR-FMS-0016" || rev[0].id === "R-FMS-0017" || rev[0].name?.includes("大三元") || rev[0].name?.includes("小四喜");
            if (isMahjong || isHu) {
              myDeck.pop(); // remove from top
              myHand.push(rev[0]);
              logBattle(`✨ 南大姊 效果：將展示的【${rev[0].name}】加入手牌！`);
              render();
            }
          }
        }
      }

      // R-FMS-0021 西南季風
      if (card.name?.includes("西南季風")) {
        const isPlayer = zone.startsWith("player_");
        const oppFront = isPlayer ? "enemy_front" : "player_front";
        const oppBack = isPlayer ? "enemy_back" : "player_back";
        const oppHand = isPlayer ? (window.XLW_ENEMY.hand || []) : hand;
        
        let targetUnit = field[oppFront][idx];
        if (targetUnit) {
          // Push front unit backward
          const existingBack = field[oppBack][idx];
          if (existingBack) {
            // Back unit is pushed off-field -> returns to hand!
            logBattle(`💥 【${existingBack.card.name}】被推擠出戰線，返回其手牌！`);
            oppHand.push(existingBack.card);
          }
          field[oppBack][idx] = targetUnit;
          targetUnit.summonedZone = oppBack;
          field[oppFront][idx] = null;
          logBattle(`✨ 西南季風 效果：推擠對手【${targetUnit.card.name}】至後排！`);
          render();
        } else {
          // Front is empty, check if back has unit -> push off-field -> returns to hand!
          targetUnit = field[oppBack][idx];
          if (targetUnit) {
            logBattle(`💥 【${targetUnit.card.name}】被推擠出戰線，返回其手牌！`);
            oppHand.push(targetUnit.card);
            field[oppBack][idx] = null;
            render();
          }
        }
      }

      // SR-FMS-0020 東北季風
      if (card.name?.includes("東北季風")) {
        const isPlayer = zone.startsWith("player_");
        const oppFront = isPlayer ? "enemy_front" : "player_front";
        const oppUnits = [];
        field[oppFront].forEach((u, i) => {
          if (u) oppUnits.push({ idx: i, name: u.card.name, unit: u });
        });
        if (oppUnits.length > 0) {
          if (isPlayer) {
            const choices = oppUnits.map(item => ({ text: `${item.name} (前排${item.idx + 1})`, value: item.idx }));
            const chosenVal = await showXLWChoiceModal("東北季風 推擠目標", "選擇一個要推擠的敵方前排單位：", choices);
            if (chosenVal !== null && chosenVal !== undefined) {
              const item = oppUnits.find(x => x.idx === chosenVal);
              const dirChoices = [{ text: "向左推擠", value: -1 }, { text: "向右推擠", value: 1 }];
              const chosenDir = await showXLWChoiceModal("東北季風 推擠方向", "請選擇推擠方向：", dirChoices);
              if (chosenDir !== null && chosenDir !== undefined) {
                const targetIdx = item.idx + chosenDir;
                if (targetIdx < 0 || targetIdx > 4) {
                  logBattle(`💥 【${item.name}】被推擠出戰線，送入墓地！`);
                  await destroyUnit(oppFront, item.idx, "enemy", false);
                } else {
                  await moveOrPushUnitToSlot(oppFront, item.idx, oppFront, targetIdx);
                }
              }
            }
          } else {
            // AI northeast push
            const item = oppUnits[Math.floor(Math.random() * oppUnits.length)];
            const pushDir = Math.random() < 0.5 ? -1 : 1;
            const targetIdx = item.idx + pushDir;
            if (targetIdx < 0 || targetIdx > 4) {
              logBattle(`💥 【${item.name}】被推擠出戰線，送入墓地！`);
              await destroyUnit(oppFront, item.idx, "player", false);
            } else {
              await moveOrPushUnitToSlot(oppFront, item.idx, oppFront, targetIdx);
            }
          }
        }
      }

      // R-FMS-0030 高塔101號
      if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
        const isPlayer = zone.startsWith("player_");
        if (isPlayer) {
          const confirm101 = await showXLWConfirm("高塔101號 效果發動", "是否展示任意張手牌以觸發被展示效果？");
          if (confirm101) {
            const choices = hand.map((c, i) => ({ text: `${c.name}`, value: i }));
            const chosen = await showXLWChoiceModal("選擇要展示的手牌", "請選擇任意卡牌展示（可多選/單選）：", choices);
            if (chosen !== null && chosen !== undefined) {
              // Note: choice modal might return single value or array depending on config, usually single choice
              await window.xlwRevealCard(hand[chosen], true);
            }
          }
        } else {
          // AI reveals its entire hand
          const oppHand = window.XLW_ENEMY.hand || [];
          for (const c of oppHand) {
            if (c) await window.xlwRevealCard(c, false);
          }
        }
      }

      // R-FMS-0031 詐胡牌
      if (card.id === "R-FMS-0031" || card.name?.includes("詐胡牌")) {
        const isPlayer = zone.startsWith("player_");
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        if (myDeck.length > 0) {
          const rev = await window.xlwRevealTopCards(1, isPlayer);
          if (rev.length > 0 && window.isMahjongUnit(rev[0])) {
            const emptySlots = isPlayer ? window.xlwGetEmptyPlayerSlots() : window.xlwGetEmptyEnemySlots();
            if (emptySlots.length > 0) {
              myDeck.pop(); // remove from top
              await window.xlwSpecialSummonUnit(rev[0], isPlayer);
              logBattle(`✨ 詐胡牌 連動效果：成功召喚【${rev[0].name}】！`);
              render();
            }
          }
        }
      }

      // R-FMS-0032 好大雞牌
      if (card.id === "R-FMS-0032" || card.name?.includes("好大雞牌")) {
        const isPlayer = zone.startsWith("player_");
        const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
        if (isPlayer) {
          const confirmChicken = await showXLWConfirm("好大雞牌 效果發動", "展示 2 張手牌（確定）還是展示牌庫頂 2 張卡牌（取消）？");
          if (confirmChicken) {
            if (myHand.length >= 2) {
              // Reveal first 2 hand cards
              await window.xlwRevealCard(myHand[0], true);
              await window.xlwRevealCard(myHand[1], true);
            } else if (myHand.length > 0) {
              await window.xlwRevealCard(myHand[0], true);
            }
          } else {
            await window.xlwRevealTopCards(2, true);
          }
        } else {
          // AI Choice
          if (Math.random() < 0.5 && myHand.length >= 2) {
            await window.xlwRevealCard(myHand[0], false);
            await window.xlwRevealCard(myHand[1], false);
          } else {
            await window.xlwRevealTopCards(2, false);
          }
        }
      }

      // SR-FMS-0036 麻祖
      if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
        const isPlayer = zone.startsWith("player_");
        const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
        const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
        
        // Find other Mahjong units on field and grave
        const graveMahjongs = myGrave.filter(c => c && window.isMahjongUnit(c));
        const fieldMahjongs = [];
        const sidePrefix = isPlayer ? "player_" : "enemy_";
        [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
          field[z].forEach((u, i) => {
            if (u && u !== field[zone][idx] && u.card && window.isMahjongUnit(u.card)) {
              fieldMahjongs.push({ zone: z, idx: i, card: u.card });
            }
          });
        });
        
        if (isPlayer) {
          const confirmMazu = await showXLWConfirm("麻祖 效果發動", "是否發動【麻祖】效果，將我方場上與墓地任意數量的其他麻將單位洗回牌庫並連續召喚？");
          if (confirmMazu) {
            let washCount = 0;
            // Wash from grave
            if (graveMahjongs.length > 0) {
              const confirmGrave = await showXLWConfirm("墓地回收", "是否回收墓地所有其他麻將單位卡？");
              if (confirmGrave) {
                graveMahjongs.forEach(c => {
                  const gIdx = graveyard.indexOf(c);
                  if (gIdx >= 0) graveyard.splice(gIdx, 1);
                  deck.push(c);
                  washCount++;
                });
              }
            }
            // Wash from field
            if (fieldMahjongs.length > 0) {
              const confirmField = await showXLWConfirm("場上回收", "是否回收場上所有其他麻將單位卡？");
              if (confirmField) {
                fieldMahjongs.forEach(item => {
                  field[item.zone][item.idx] = null;
                  deck.push(item.card);
                  washCount++;
                });
              }
            }
            if (washCount > 0) {
              shuffle(deck);
              logBattle(`✨ 麻祖 效果：回收了 ${washCount} 張麻將卡洗回牌庫，準備連續召喚！`);
              const rev = await window.xlwRevealTopCards(washCount, true);
              for (const c of rev) {
                if (window.isMahjongUnit(c)) {
                  const emptySlots = window.xlwGetEmptyPlayerSlots();
                  if (emptySlots.length > 0) {
                    const dIdx = deck.indexOf(c);
                    if (dIdx >= 0) deck.splice(dIdx, 1);
                    await window.xlwSpecialSummonUnit(c, true);
                  }
                }
              }
              render();
            }
          }
        } else {
          // AI Ma Zu
          let washCount = 0;
          graveMahjongs.forEach(c => {
            const gIdx = myGrave.indexOf(c);
            if (gIdx >= 0) myGrave.splice(gIdx, 1);
            myDeck.push(c);
            washCount++;
          });
          fieldMahjongs.forEach(item => {
            field[item.zone][item.idx] = null;
            myDeck.push(item.card);
            washCount++;
          });
          if (washCount > 0) {
            shuffle(myDeck);
            logBattle(`✨ 對手 麻祖 效果：回收了 ${washCount} 張麻將卡洗回其牌庫！`);
            const rev = await window.xlwRevealTopCards(washCount, false);
            for (const c of rev) {
              if (window.isMahjongUnit(c)) {
                const emptySlots = window.xlwGetEmptyEnemySlots();
                if (emptySlots.length > 0) {
                  const dIdx = myDeck.indexOf(c);
                  if (dIdx >= 0) myDeck.splice(dIdx, 1);
                  await window.xlwSpecialSummonUnit(c, false);
                }
              }
            }
            render();
          }
        }
      }

      // R-CAT-0042 / SSR-CAT-0042 魔拳喵喵"""

    safe_replace("performSummonToSlot Happy Island Immediates", target_summon_happy, replacement_summon_happy)

    # 10. Active clicks for 導遊姐姐 (R-FMS-0034)
    target_active_happy = """            // (o-beibei) 背背獸人 R-ORC-0042 / R-ORC-0042-繪畫 合體寄生主動技能"""

    replacement_active_happy = """            // (o-tourguide) 導遊姐姐 主動技能
            if (obj.card.id === "R-FMS-0034" || obj.card.id === "SSR-FMS-0034" || obj.card.id === "SSR-FMS-0034-金" || obj.card.name?.includes("導遊姐姐")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.tourGuideUsedTurn === turn) {
                setStatus("導遊姐姐 的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmShuffle = await showXLWConfirm("導遊姐姐 效果發動", "是否在展示牌庫頂卡牌前重洗牌庫？");
              if (confirmShuffle) {
                const myDeck = zone.startsWith("player_") ? deck : (window.XLW_ENEMY.deck || []);
                shuffle(myDeck);
                logBattle("✨ 導遊姐姐 效果：重洗我方牌庫！");
              }
              await window.xlwRevealTopCards(1, zone.startsWith("player_"));
              obj.tourGuideUsedTurn = turn;
              render();
              if (isMultiplayer) {
                sendFullGameStateToOpponent();
              }
              return;
            }

            // (o-beibei) 背背獸人 R-ORC-0042 / R-ORC-0042-繪畫 合體寄生主動技能"""

    safe_replace("Player Active click for Tour Guide", target_active_happy, replacement_active_happy)

    # 10.2 AI Active click for Tour Guide inside runEnemyTurn
    target_ai_active_happy = """    // AI 背背獸人 (R-ORC-0042 / R-ORC-0042-繪畫) 效果發動"""

    replacement_ai_active_happy = """    // AI 導遊姐姐 (R-FMS-0034) 效果發動
    const aiGuides = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "R-FMS-0034" || u.card.id === "SSR-FMS-0034" || u.card.id === "SSR-FMS-0034-金" || u.card.name?.includes("導遊姐姐"))) {
          if (!window.isUnitSilenced(u, z, i) && u.tourGuideUsedTurn !== turn) {
            aiGuides.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    }
    for (const g of aiGuides) {
      const myDeck = window.XLW_ENEMY.deck || [];
      shuffle(myDeck);
      logBattle("✨ 對手 導遊姐姐 效果：重洗對手牌庫，並展示 1 張牌！");
      await window.xlwRevealTopCards(1, false);
      g.unit.tourGuideUsedTurn = turn;
      render();
    }

    // AI 背背獸人 (R-ORC-0042 / R-ORC-0042-繪畫) 效果發動"""

    safe_replace("AI Active click for Tour Guide", target_ai_active_happy, replacement_ai_active_happy)

    # 11. castSpell combos: 小四喜 / 大三元 / 詐胡 / 聽牌
    target_combo_spells = """  } else if (card.id === "ORC-0019" || card.name.includes("天下第一獸人作弊大會")) {"""

    replacement_combo_spells = """  } else if (card.id === "R-FMS-0017" || card.name?.includes("小四喜")) {
    const ok = window.xlwCheckMahjongCombo(true, "小四喜");
    if (!ok) {
      setStatus("我方場上未備齊東、南、西、北，無法發動小四喜！");
      return;
    }
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    await castSpellChain(spellCard, async () => {
      playerBonusScore += 8;
      exileCard(spellCard);
      logBattle("✨ 小四喜 效果發動：我方成功胡牌，額外分數 +8★！此卡被除外。");
      renderScore();
      render();
    });
  } else if (card.id === "SR-FMS-0016" || card.name?.includes("大三元")) {
    const ok = window.xlwCheckMahjongCombo(true, "大三元");
    if (!ok) {
      setStatus("我方場上未備齊紅中、白板、發財，無法發動大三元！");
      return;
    }
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    await castSpellChain(spellCard, async () => {
      playerBonusScore += 8;
      exileCard(spellCard);
      logBattle("✨ 大三元 效果發動：我方成功胡牌，額外分數 +8★！此卡被除外。");
      renderScore();
      render();
    });
  } else if (card.id === "R-FMS-0019" || card.name?.includes("詐胡")) {
    const mahjongs = [];
    for (const z of ["player_front", "player_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && window.isMahjongUnit(u.card)) {
          mahjongs.push({ zone: z, idx: i, name: u.card.name });
        }
      });
    }
    if (mahjongs.length === 0) {
      setStatus("我方場上沒有任何麻將單位可供發動詐胡！");
      return;
    }
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    await castSpellChain(spellCard, async () => {
      const choices = mahjongs.map((item, i) => ({ text: `${item.name} (${item.zone.includes("front") ? "前排" : "後排"}${item.idx + 1})`, value: i }));
      const chosen = await showXLWChoiceModal("選擇詐胡目標", "請選擇要變更名稱的麻將單位：", choices);
      if (chosen !== null && chosen !== undefined) {
        const target = mahjongs[chosen];
        const names = ["東大哥", "南大姊", "西小弟", "北小妹", "紅中哥", "白板哥", "發財哥", "萬字大叔"];
        const nameChoices = names.map((n, i) => ({ text: n, value: i }));
        const chosenNameIdx = await showXLWChoiceModal("宣告卡名", "請選擇要宣告的卡名：", nameChoices);
        if (chosenNameIdx !== null && chosenNameIdx !== undefined) {
          const newName = names[chosenNameIdx];
          const targetUnit = field[target.zone][target.idx];
          targetUnit.originalName = targetUnit.card.name;
          targetUnit.card.name = newName;
          logBattle(`✨ 詐胡 效果：【${target.name}】更名為【${newName}】直到回合結束！`);
          render();
        }
      }
    });
  } else if (card.id === "R-FMS-0018" || card.name?.includes("聽牌")) {
    const myHuCards = hand.filter(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
    if (myHuCards.length === 0) {
      setStatus("我方手牌中沒有大三元或小四喜等胡牌！");
      return;
    }
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    await castSpellChain(spellCard, async () => {
      const choices = myHuCards.map((c, i) => ({ text: `${c.name}`, value: i }));
      const chosen = await showXLWChoiceModal("選擇展示的胡牌", "請選擇展示的胡牌卡：", choices);
      if (chosen !== null && chosen !== undefined) {
        const hu = myHuCards[chosen];
        await window.xlwRevealCard(hu, true);
        
        // Show other cards in hand mentioned in Hu description
        const required = hu.name?.includes("大三元") ? ["紅中哥", "白板哥", "發財哥"] : ["東大哥", "北小妹", "西小弟", "南大姊"];
        const toReveal = [];
        required.forEach(req => {
          const inHand = hand.find(c => c && c.name?.includes(req));
          if (inHand) toReveal.push(inHand);
        });
        
        for (const c of toReveal) {
          await window.xlwRevealCard(c, true);
        }
        
        // Reveal top of deck
        const revDeck = await window.xlwRevealTopCards(1, true);
        
        // Check if all required cards are now revealed or on field
        let ok = true;
        const namesOnFieldAndRevealed = [];
        for (const z of ["player_front", "player_back"]) {
          field[z].forEach(u => {
            if (u && u.card) namesOnFieldAndRevealed.push(u.card.name);
          });
        }
        toReveal.forEach(c => namesOnFieldAndRevealed.push(c.name));
        revDeck.forEach(c => namesOnFieldAndRevealed.push(c.name));
        
        required.forEach(req => {
          if (!namesOnFieldAndRevealed.some(n => n && n.includes(req))) ok = false;
        });
        
        if (ok) {
          logBattle("✨ 聽牌 成功！所有提及的麻將單位均在場上或已被展示，額外特殊召喚展示的單位卡！");
          const emptySlots = window.xlwGetEmptyPlayerSlots();
          
          // Special summon any revealed units that are in hand or deck
          const unitsToSummon = [];
          toReveal.forEach(c => {
            if (c.type === "unit") unitsToSummon.push(c);
          });
          revDeck.forEach(c => {
            if (c.type === "unit" && !unitsToSummon.includes(c)) unitsToSummon.push(c);
          });
          
          for (const c of unitsToSummon) {
            const hIdx = hand.indexOf(c);
            if (hIdx >= 0) hand.splice(hIdx, 1);
            const dIdx = deck.indexOf(c);
            if (dIdx >= 0) deck.splice(dIdx, 1);
            
            const success = await window.xlwSpecialSummonUnit(c, true);
            if (!success) break;
          }
          render();
        } else {
          logBattle("聽牌 效果結束：未湊齊所有對應的麻將單位。");
        }
      }
    });
  } else if (card.id === "R-FMS-0023" || card.name?.includes("星駭隧道")) {
    const spellCard = hand.splice(handIndex, 1)[0];
    await showSpellActivationOverlay(spellCard, "player");
    await castSpellChain(spellCard, async () => {
      const rev = await window.xlwRevealTopCards(1, true);
      if (rev.length > 0 && rev[0].type === "unit") {
        const revAtk = rev[0].attack ?? rev[0].atk ?? rev[0].power ?? 0;
        let count = 0;
        for (const z of ["enemy_front", "enemy_back"]) {
          field[z].forEach(u => {
            if (u && u.attacking) {
              const uAtk = getUnitAtk(u);
              if (uAtk <= revAtk) {
                u.attacking = false;
                u.tapped = false;
                u.target = null;
                count++;
              }
            }
          });
        }
        if (count > 0) {
          logBattle(`✨ 星駭隧道：對手有 ${count} 個進攻單位被迫轉正取消進攻！`);
          render();
        }
      }
    });
  } else if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
    // Check exile zone
    const hasHu = exileZone.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
    if (!hasHu) {
      setStatus("除外區沒有大三元或小四喜等胡牌，無法打出麻祖！");
      return;
    }
    // Proceed with regular unit play
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
    const ok = window.xlwCheckMahjongCombo(true, "小四喜");
    if (!ok) {
      setStatus("我方場上未備齊東、南、西、北，無法召喚高塔101號！");
      return;
    }
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0031" || card.id === "R-FMS-0032" || card.id === "R-FMS-0033" || card.id === "R-FMS-0034" || card.id === "SR-FMS-0033") {
    // Normal Happy Island unit play
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0021" || card.name?.includes("西南季風") || card.name?.includes("東北季風")) {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0007" || card.id === "R-FMS-0009" || card.id === "R-FMS-0010" || card.id === "R-FMS-0011") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0013" || card.id === "R-FMS-0014" || card.id === "R-FMS-0015") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0001" || card.id === "R-FMS-0002" || card.id === "R-FMS-0005" || card.id === "R-FMS-0006") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0026" || card.id === "R-FMS-0027" || card.id === "R-FMS-0029" || card.id === "SR-FMS-0004") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "SR-FMS-0025" || card.id === "SR-FMS-0028" || card.id === "SR-FMS-0020") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0022" || card.id === "SR-FMS-0036") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "R-FMS-0012") {
    await performSummonToSlot(card, handIndex);
  } else if (card.id === "ORC-0019" || card.name.includes("天下第一獸人作弊大會")) {"""

    safe_replace("castSpell combos for Happy Island", target_combo_spells, replacement_combo_spells)

    # 12. AI cast spells in aiPlayMagicCardsSummonPhase
    target_ai_magic_happy = """  // 天下第一獸人作弊大會 (ORC-0019)"""

    replacement_ai_magic_happy = """  // AI 大三元 (SR-FMS-0016)
  const tripleIdx = hand.findIndex(c => c && (c.id === "SR-FMS-0016" || c.name?.includes("大三元")));
  if (tripleIdx >= 0 && window.xlwCheckMahjongCombo(false, "大三元")) {
    const spellCard = hand.splice(tripleIdx, 1)[0];
    await xlwShowSpellActivationOverlay(spellCard, "enemy");
    await aiCastSpell(spellCard, async () => {
      enemyBonusScore += 8;
      enemyExileZone.push(spellCard);
      logBattle("✨ 對手 AI 大三元 效果發動：對手成功胡牌，額外分數 +8★！此卡被除外。");
      renderScore();
      render();
    });
  }

  // AI 小四喜 (R-FMS-0017)
  const fourIdx = hand.findIndex(c => c && (c.id === "R-FMS-0017" || c.name?.includes("小四喜")));
  if (fourIdx >= 0 && window.xlwCheckMahjongCombo(false, "小四喜")) {
    const spellCard = hand.splice(fourIdx, 1)[0];
    await xlwShowSpellActivationOverlay(spellCard, "enemy");
    await aiCastSpell(spellCard, async () => {
      enemyBonusScore += 8;
      enemyExileZone.push(spellCard);
      logBattle("✨ 對手 AI 小四喜 效果發動：對手成功胡牌，額外分數 +8★！此卡被除外。");
      renderScore();
      render();
    });
  }

  // 天下第一獸人作弊大會 (ORC-0019)"""

    safe_replace("AI magic spells happy island", target_ai_magic_happy, replacement_ai_magic_happy)

    # 13. AI unit play limits (Mahjong wildcard check for High Tower and Ma Zu)
    target_ai_unit_play = """async function aiPlayUnits() {
  if (window.XLW_enemySummonCountThisTurn >= enemySummonLimit) return;"""

    replacement_ai_unit_play = """async function aiPlayUnits() {
  if (window.XLW_enemySummonCountThisTurn >= enemySummonLimit) return;

  // AI check High Tower 101 play eligibility
  const towerIdx = hand.findIndex(c => c && (c.id === "R-FMS-0030" || c.id === "SSR-FMS-0030" || c.name?.includes("高塔101號")));
  if (towerIdx >= 0) {
    const ok = window.xlwCheckMahjongCombo(false, "小四喜");
    if (!ok) {
      // Temporarily swap it to the end of hand so AI won't try to play it
      const tower = hand.splice(towerIdx, 1)[0];
      hand.push(tower);
    }
  }
  
  // AI check Ma Zu SR-FMS-0036 play eligibility
  const mazuIdx = hand.findIndex(c => c && (c.id === "SR-FMS-0036" || c.name?.includes("麻祖")));
  if (mazuIdx >= 0) {
    const hasHu = enemyExileZone.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
    if (!hasHu) {
      const mazu = hand.splice(mazuIdx, 1)[0];
      hand.push(mazu);
    }
  }"""

    safe_replace("AI unit play limits", target_ai_unit_play, replacement_ai_unit_play)

    # 14. Restore Mahjong unit names after turn end
    target_turn_end_restore = """  // Reset temporary flags or counters if needed
  window.XLW_currentFoodBallIdx = null;"""

    replacement_turn_end_restore = """  // Reset temporary flags or counters if needed
  window.XLW_currentFoodBallIdx = null;
  
  // Restore Mahjong original names
  for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
    field[z].forEach(u => {
      if (u && u.originalName) {
        u.card.name = u.originalName;
        u.originalName = null;
      }
    });
  }"""

    safe_replace("Restore Mahjong unit names after turn end", target_turn_end_restore, replacement_turn_end_restore)

    # Save the modified code back to static/game_v8.js
    open(filepath, "w", encoding="utf-8").write(code)
    print("All Happy Island changes written successfully.")

if __name__ == '__main__':
    main()
