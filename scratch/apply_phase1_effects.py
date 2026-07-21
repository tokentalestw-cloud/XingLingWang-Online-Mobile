# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = 'static/game_v8.js'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

# Define the helper functions to insert above function confirmTribute()
helpers_code = """
async function moveOrPushUnitToSlot(fromZone, fromIdx, toZone, toIdx) {
  const movingUnit = field[fromZone][fromIdx];
  if (!movingUnit) return;
  
  const existingUnit = field[toZone][toIdx];
  if (existingUnit) {
    if (toZone.includes("front")) {
      const backZone = toZone.replace("front", "back");
      const existingBack = field[backZone][toIdx];
      if (existingBack) {
        logBattle(`💥 ${existingBack.card.name} 被推擠出戰線送入墓地！`);
        await destroyUnit(backZone, toIdx, backZone.startsWith("player_") ? "player" : "enemy", false);
      }
      field[backZone][toIdx] = existingUnit;
      if (field[backZone][toIdx]) {
        field[backZone][toIdx].summonedZone = backZone;
      }
    } else {
      logBattle(`💥 ${existingUnit.card.name} 被推擠出戰線送入墓地！`);
      await destroyUnit(toZone, toIdx, toZone.startsWith("player_") ? "player" : "enemy", false);
    }
  }
  field[toZone][toIdx] = movingUnit;
  if (field[toZone][toIdx]) {
    field[toZone][toIdx].summonedZone = toZone;
  }
  field[fromZone][fromIdx] = null;
  render();
}

window.xlwPlayerTributeUnit = async function(unit, zone, idx) {
  if (unit.card.name.includes("小旅人") || unit.card.id === "TOKEN_TRAVELER") {
    logBattle(`✨ ${unit.card.name} 作為祭品被獻祭，直接返回森林。`);
  } else {
    // Check for Accident Property (事故物件)
    if (unit.accidentProperty || (unit.equipments && unit.equipments.includes("事故物件"))) {
      const oppGrave = window.XLW_ENEMY.grave || [];
      const yokaiInGrave = oppGrave.filter(c => c && (c.faction === "妖怪村莊" || c.id?.includes("VLG")));
      if (yokaiInGrave.length > 0) {
        const chosen = yokaiInGrave[Math.floor(Math.random() * yokaiInGrave.length)];
        oppGrave.splice(oppGrave.indexOf(chosen), 1);
        window.XLW_ENEMY.hand.push(chosen);
        logBattle(`✨ 對手 事故物件 效果：對手將其墓地中的【${chosen.name}】回收至其手牌！`);
      }
    }

    const hasPriest = ["player_front", "player_back"].some(z => field[z].some((u, i) => u && u.card && (u.card.id === "R-VLG-0043" || u.card.name.includes("恐怖祭司")) && !window.isUnitSilenced(u, z, i)));
    let exiled = false;
    if (hasPriest && (unit.card.id !== "R-VLG-0043" && !unit.card.name.includes("恐怖祭司")) && (unit.card.faction === "妖怪村莊" || unit.card.id?.includes("VLG"))) {
      const targetCost = getCardTributeCost(unit.card);
      const eligibleGrave = graveyard.filter(c => c && c.type === "unit" && (c.faction === "妖怪村莊" || c.id?.includes("VLG")) && getCardTributeCost(c) === targetCost);
      if (eligibleGrave.length > 0) {
        const usePriest = await showXLWConfirm("恐怖祭司 效果發動", `是否將被獻祭的【${unit.card.name}】改為除外，並從墓地復活 1 個祭品數為 ${targetCost} 的妖怪村莊單位？`);
        if (usePriest) {
          exileCard(unit.card, "player");
          exiled = true;
          const choices = eligibleGrave.map((c, i) => ({ text: `${c.name} (${c.id})`, value: i }));
          const chosenGraveIdx = await showXLWChoiceModal("恐怖祭司 復活選擇", "選擇復活的單位：", choices);
          if (chosenGraveIdx !== null && chosenGraveIdx !== undefined) {
            const resurrectedCard = eligibleGrave[chosenGraveIdx];
            graveyard.splice(graveyard.indexOf(resurrectedCard), 1);
            const emptySlots = [];
            for (const z of ["player_front", "player_back"]) {
              field[z].forEach((slotUnit, slotIdx) => {
                if (!slotUnit) emptySlots.push({ zone: z, idx: slotIdx });
              });
            }
            if (emptySlots.length > 0) {
              const chosenSlot = emptySlots[0];
              field[chosenSlot.zone][chosenSlot.idx] = {
                card: resurrectedCard,
                tapped: false,
                attacking: false,
                target: null,
                summonedTurn: turn,
                summonedZone: chosenSlot.zone
              };
              logBattle(`✨ 恐怖祭司 效果：特殊召喚了墓地中的【${resurrectedCard.name}】！`);
            }
          }
        }
      }
    }
    if (!exiled) {
      graveyard.push(unit.card);
    }
  }
};

window.xlwEnemyTributeUnit = async function(unit, zone, idx) {
  if (unit.card.name.includes("小旅人") || unit.card.id === "TOKEN_TRAVELER") {
    logBattle(`✨ 對手 ${unit.card.name} 作為祭品被獻祭，直接返回森林。`);
  } else {
    // Check for Accident Property (事故物件)
    if (unit.accidentProperty || (unit.equipments && unit.equipments.includes("事故物件"))) {
      const yokaiInGrave = graveyard.filter(c => c && (c.faction === "妖怪村莊" || c.id?.includes("VLG")));
      if (yokaiInGrave.length > 0) {
        const choices = yokaiInGrave.map((c, i) => ({ text: c.name, value: i }));
        const chosenIdxVal = await showXLWChoiceModal("事故物件 效果發動", "選擇回到我方手牌的妖怪村莊卡牌：", choices);
        if (chosenIdxVal !== null && chosenIdxVal !== undefined) {
          const chosen = yokaiInGrave[chosenIdxVal];
          graveyard.splice(graveyard.indexOf(chosen), 1);
          hand.push(chosen);
          logBattle(`✨ 事故物件 效果：我方將墓地中的【${chosen.name}】回收至手牌！`);
        }
      }
    }

    const oppGrave = window.XLW_ENEMY.grave || [];
    const hasPriest = ["enemy_front", "enemy_back"].some(z => field[z].some((u, i) => u && u.card && (u.card.id === "R-VLG-0043" || u.card.name.includes("恐怖祭司")) && !window.isUnitSilenced(u, z, i)));
    let exiled = false;
    if (hasPriest && (unit.card.id !== "R-VLG-0043" && !unit.card.name.includes("恐怖祭司")) && (unit.card.faction === "妖怪村莊" || unit.card.id?.includes("VLG"))) {
      const targetCost = getCardTributeCost(unit.card);
      const eligibleGrave = oppGrave.filter(c => c && c.type === "unit" && (c.faction === "妖怪村莊" || c.id?.includes("VLG")) && getCardTributeCost(c) === targetCost);
      if (eligibleGrave.length > 0) {
        exileCard(unit.card, "enemy");
        exiled = true;
        const resurrectedCard = eligibleGrave[Math.floor(Math.random() * eligibleGrave.length)];
        oppGrave.splice(oppGrave.indexOf(resurrectedCard), 1);
        const emptySlots = [];
        for (const z of ["enemy_front", "enemy_back"]) {
          field[z].forEach((slotUnit, slotIdx) => {
            if (!slotUnit) emptySlots.push({ zone: z, idx: slotIdx });
          });
        }
        if (emptySlots.length > 0) {
          const chosenSlot = emptySlots[0];
          field[chosenSlot.zone][chosenSlot.idx] = {
            card: resurrectedCard,
            tapped: false,
            attacking: false,
            target: null,
            summonedTurn: turn,
            summonedZone: chosenSlot.zone
          };
          logBattle(`✨ 對手 恐怖祭司 效果：特殊召喚了墓地中的【${resurrectedCard.name}】！`);
        }
      }
    }
    if (!exiled) {
      oppGrave.push(unit.card);
    }
  }
};
"""

# 1. Insert helper code above confirmTribute()
target_confirm = "function confirmTribute() {"
if target_confirm in code:
    code = code.replace(target_confirm, helpers_code + "\n" + target_confirm, 1)
    print("Success: Inserted helper functions above confirmTribute().")
else:
    print("Error: confirmTribute() target not found!")
    sys.exit(1)

# 2. Modify xlwIsEnemySummonCard to support new cards
target_enemy_sum = 'if (c.id === "CAT-0012" || c.name?.includes("喵玩具") || c.id === "R-CAT-0043" || c.name?.includes("喵喵球")) return true;'
replacement_enemy_sum = 'if (c.id === "CAT-0012" || c.name?.includes("喵玩具") || c.id === "R-CAT-0043" || c.name?.includes("喵喵球") || c.id === "R-VLG-0036" || c.name?.includes("人臉魚") || c.id === "R-VLG-0045" || c.name?.includes("殭屍女") || c.id === "R-VLG-0046" || c.name?.includes("背後靈") || c.id === "R-CAT-0037" || c.name?.includes("喵抓板")) return true;'
if target_enemy_sum in code:
    code = code.replace(target_enemy_sum, replacement_enemy_sum, 1)
    print("Success: Updated xlwIsEnemySummonCard.")
else:
    print("Error: xlwIsEnemySummonCard target not found!")
    sys.exit(1)

# 3. Modify xlwCanSummonToZone
target_can_sum_zone = """  if (canSummonToEnemy) {
    if (zone === "enemy_front") return true;
    if (zone === "enemy_back") {
      if (window.XLW_enemyYouCantSeeMeActiveTurn === turn) {
        return true;
      }
      const enemyFrontHasEmpty = field.enemy_front.some(u => !u);
      return !enemyFrontHasEmpty;
    }
    return false;
  }"""
replacement_can_sum_zone = """  if (canSummonToEnemy) {
    if (zone === "enemy_front" || zone === "player_front") return true;
    if (zone === "enemy_back" || zone === "player_back") {
      if (c && (c.id === "R-VLG-0046" || c.name?.includes("背後靈"))) return true;
      if (window.XLW_enemyYouCantSeeMeActiveTurn === turn || window.XLW_playerYouCantSeeMeActiveTurn === turn) {
        return true;
      }
      const targetSide = zone.startsWith("player_") ? "player" : "enemy";
      const frontZone = targetSide === "player" ? "player_front" : "enemy_front";
      const frontHasEmpty = field[frontZone].some(u => !u);
      return !frontHasEmpty;
    }
    return false;
  }"""
if target_can_sum_zone in code:
    code = code.replace(target_can_sum_zone, replacement_can_sum_zone, 1)
    print("Success: Updated xlwCanSummonToZone.")
else:
    print("Error: xlwCanSummonToZone target block not found!")
    sys.exit(1)

# 4. Modify destroyUnit to handle escape (逃脫), water ghost (水鬼) and countdown車站 protection (with exact 6 spaces indentation match)
target_destroy_sparks = """      const sparks = document.createElement("div");
      sparks.className = "shatter-sparks";
      slot.appendChild(sparks);"""

replacement_destroy_sparks = """      const sparks = document.createElement("div");
      sparks.className = "shatter-sparks";
      slot.appendChild(sparks);

      // 1. 如月車站 生死倒數保護
      if (unit.card.id === "R-VLG-0018" || unit.card.name?.includes("如月車站")) {
        if (countdownActive) {
          logBattle("✨ 如月車站 效果：生死倒數階段此卡不會被破壞！");
          if (sparks) sparks.remove();
          return;
        }
      }

      // 2. 逃脫 效果阻斷送墓
      if (isCombatDestruction) {
        if (owner === "player" && window.XLW_playerCatEscapeTurn === turn) {
          hand.push(unit.card);
          logBattle(`✨ 逃脫 效果：被破壞的單位【${unit.card.name}】回到手牌！`);
          field[zone][idx] = null;
          if (sparks) sparks.remove();
          render();
          return;
        }
        if (owner === "enemy" && window.XLW_enemyCatEscapeTurn === turn) {
          if (!window.XLW_ENEMY) window.XLW_ENEMY = { hand: [] };
          if (!window.XLW_ENEMY.hand) window.XLW_ENEMY.hand = [];
          window.XLW_ENEMY.hand.push(unit.card);
          logBattle(`✨ 對手 逃脫 效果：被破壞的單位【${unit.card.name}】回到對手手牌！`);
          field[zone][idx] = null;
          if (sparks) sparks.remove();
          render();
          return;
        }
      }

      // 3. 水鬼 效果觸發 (戰鬥與效果破壞之同歸於盡)
      if (unit.card.id === "R-VLG-0038" || unit.card.name?.includes("水鬼")) {
        const isPlayer = zone.startsWith("player_");
        const oppOwner = isPlayer ? "enemy" : "player";
        const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
        
        if (isCombatDestruction) {
          let oppUnit = null;
          let oppZone = null;
          for (const z of oppZones) {
            if (field[z][idx]) {
              oppUnit = field[z][idx];
              oppZone = z;
              break;
            }
          }
          if (oppUnit) {
            logBattle(`✨ 水鬼 效果發動：與敵方單位【${oppUnit.card.name}】同歸於盡！`);
            await destroyUnit(oppZone, idx, oppOwner, false, false);
          }
        } else if (window.XLW_currentEffectSourceUnit) {
          const src = window.XLW_currentEffectSourceUnit;
          let srcZone = null;
          let srcIdx = -1;
          for (const z of oppZones) {
            const i = field[z].indexOf(src);
            if (i >= 0) {
              srcZone = z;
              srcIdx = i;
              break;
            }
          }
          if (srcZone && srcIdx >= 0) {
            logBattle(`✨ 水鬼 效果發動：使破壞牠的敵方單位【${src.card.name}】被破壞！`);
            await destroyUnit(srcZone, srcIdx, oppOwner, false, false);
          }
        }
      }
"""
if target_destroy_sparks in code:
    code = code.replace(target_destroy_sparks, replacement_destroy_sparks, 1)
    print("Success: Updated destroyUnit sparks block.")
else:
    print("Error: destroyUnit sparks block not found!")
    sys.exit(1)

# 4b. Clear stored units when 如月車站 is actually destroyed
target_destroy_exile = """  } else if (shouldExile) {
    logBattle(`✨ 被擊破的 ${unit.card.name} 被除外（不進入墓地）！`);
    exileCard(unit.card, owner);
  } else {"""
replacement_destroy_exile = """  } else if (shouldExile) {
    logBattle(`✨ 被擊破的 ${unit.card.name} 被除外（不進入墓地）！`);
    exileCard(unit.card, owner);
  } else {
    // 如月車站 被破壞時釋放/破壞封存單位
    if (unit.card.id === "R-VLG-0018" || unit.card.name?.includes("如月車站")) {
      if (unit.storedUnits && unit.storedUnits.length > 0) {
        logBattle(`✨ 如月車站 效果：被破壞時，封存於其下方的 ${unit.storedUnits.length} 個單位也隨之被破壞送入墓地！`);
        unit.storedUnits.forEach(c => {
          if (owner === "player") {
            graveyard.push(c);
          } else {
            if (!window.XLW_ENEMY) window.XLW_ENEMY = { grave: [] };
            if (!window.XLW_ENEMY.grave) window.XLW_ENEMY.grave = [];
            window.XLW_ENEMY.grave.push(c);
          }
        });
        unit.storedUnits = [];
      }
    }
"""
if target_destroy_exile in code:
    code = code.replace(target_destroy_exile, replacement_destroy_exile, 1)
    print("Success: Updated destroyUnit station clear logic.")
else:
    print("Error: destroyUnit station clear logic target not found!")
    sys.exit(1)

# 5. Update confirmTribute() player sacrifice flow to record last sacrificed cards and use helper (with weird indentation match)
target_player_sac = """  if (unit.card.name.includes("小旅人") || unit.card.id === "TOKEN_TRAVELER") {
          logBattle(`✨ ${unit.card.name} 作為祭品被獻祭，直接返回森林。`);
        } else {
          graveyard.push(unit.card);
        }
        field[t.zone][t.idx] = null;"""
replacement_player_sac = """  if (unit.card.name.includes("小旅人") || unit.card.id === "TOKEN_TRAVELER") {
          logBattle(`✨ ${unit.card.name} 作為祭品被獻祭，直接返回森林。`);
        } else {
          window.XLW_lastSacrificedCards = selectedTributes.map(t2 => {
            if (t2.zone === "dummy") return null;
            return field[t2.zone][t2.idx] ? field[t2.zone][t2.idx].card : null;
          }).filter(Boolean);
          
          await window.xlwPlayerTributeUnit(unit, t.zone, t.idx);
        }
        field[t.zone][t.idx] = null;"""
if target_player_sac in code:
    code = code.replace(target_player_sac, replacement_player_sac, 1)
    print("Success: Updated player sacrifice flow in confirmTribute().")
else:
    print("Error: player sacrifice flow target not found!")
    sys.exit(1)

# 5b. Zombie girl trigger when player confirmTribute finishes
target_confirm_then = """  executeTributeEffects().then(async () => {
    // 記錄被獻祭的祭品位置，供聯網召喚同步清除
    window.XLW_lastTributes = selectedTributes.map(t => ({ zone: t.zone, idx: t.idx }));"""
replacement_confirm_then = """  executeTributeEffects().then(async () => {
    // 記錄被獻祭的祭品位置，供聯網召喚同步清除
    window.XLW_lastTributes = selectedTributes.map(t => ({ zone: t.zone, idx: t.idx }));
    
    // 觸發對手墓地中的殭屍女 (R-VLG-0045)
    const oppGrave = window.XLW_ENEMY.grave || [];
    const zombieIdx = oppGrave.findIndex(c => c && (c.id === "R-VLG-0045" || c.name.includes("殭屍女")));
    if (zombieIdx >= 0) {
      const emptySlots = [];
      for (const z of ["player_front", "player_back"]) {
        field[z].forEach((u, i) => { if (!u) emptySlots.push({ zone: z, idx: i }); });
      }
      if (emptySlots.length > 0) {
        const slot = emptySlots[0];
        const zombieCard = oppGrave.splice(zombieIdx, 1)[0];
        field[slot.zone][slot.idx] = {
          card: zombieCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: slot.zone
        };
        logBattle(`✨ 對手 殭屍女 效果：從對手墓地特殊召喚【殭屍女】至我方場上！`);
        render();
      }
    }"""
if target_confirm_then in code:
    code = code.replace(target_confirm_then, replacement_confirm_then, 1)
    print("Success: Added Zombie girl trigger to confirmTribute.")
else:
    print("Error: confirmTribute then target not found!")
    sys.exit(1)

# 6. Add startTributeSummon tactical phase bypass check
target_start_trib_phase = """  if (phase === "戰術佈陣") {
    setStatus("戰術佈陣階段只能召喚免祭品單位或小旅人，不能進行獻祭召喚。");
    return;
  }"""
replacement_start_trib_phase = """  if (phase === "戰術佈陣" && !window.XLW_playerCurseSummonActive && !window.XLW_playerFacelessManActive) {
    setStatus("戰術佈陣階段只能召喚免祭品單位或小旅人，不能進行獻祭召喚。");
    return;
  }
  if (phase === "戰術佈陣") {
    if (tacticalSummonUsed) {
      setStatus("本回合戰術佈陣階段已進行過召喚。");
      return;
    }
  }"""
if target_start_trib_phase in code:
    code = code.replace(target_start_trib_phase, replacement_start_trib_phase, 1)
    print("Success: Updated startTributeSummon phase check.")
else:
    print("Error: startTributeSummon phase check target not found!")
    sys.exit(1)

# 6b. Set tacticalSummonUsed = true and consume curse/faceless when tribute summon finishes (with 4 spaces indentation match)
target_confirm_trib_finish = """    const targetIdx = selectedHandForTribute;
    tributeWaitingPosition = true;
    selectedHandForSummon = targetIdx;"""
replacement_confirm_trib_finish = """    const targetIdx = selectedHandForTribute;
    tributeWaitingPosition = true;
    selectedHandForSummon = targetIdx;
    if (phase === "戰術佈陣") {
      tacticalSummonUsed = true;
      if (window.XLW_playerCurseSummonActive) {
        window.XLW_playerCurseSummonActive = false;
        logBattle("✨ 詛咒通靈 效果：已使用此效果進行了獻祭召喚！");
      }
    }"""
if target_confirm_trib_finish in code:
    code = code.replace(target_confirm_trib_finish, replacement_confirm_trib_finish, 1)
    print("Success: Updated confirmTribute finish flag.")
else:
    print("Error: confirmTribute finish flag target not found!")
    sys.exit(1)

# 7. Add Yokai Village tribute effects to executeTributeEffects loop
target_tribute_loop_start = """    for (const t of selectedTributes) {
      if (t.zone === "dummy") continue; \n      const unit = field[t.zone][t.idx];
      if (unit && unit.card) {"""
tribute_effects_body = """
        // (f-1) 紅衣女孩: 移動1個無須祭品的敵方單位到正前方
        if (unit.card.id === "R-VLG-0034" || unit.card.name.includes("紅衣女孩")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
          const targetCol = t.idx;
          const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
          
          if (isPlayer) {
            const oppTributeFree = [];
            for (const oz of oppZones) {
              field[oz].forEach((u, idx) => {
                if (u && u.card && getCardTributeCost(u.card) === 0) {
                  oppTributeFree.push({ zone: oz, idx, name: u.card.name, unit: u });
                }
              });
            }
            if (oppTributeFree.length > 0) {
              const choices = oppTributeFree.map((item, idx) => ({ text: `${item.name} (${item.zone === "enemy_front" ? "前" : "後"}${item.idx + 1})`, value: idx }));
              const chosenVal = await showXLWChoiceModal("紅衣女孩 獻祭效果", "請選擇要拉到其正前方的敵方單位：", choices);
              if (chosenVal !== null && chosenVal !== undefined) {
                const item = oppTributeFree[chosenVal];
                logBattle(`✨ 紅衣女孩 效果：拉動對手的【${item.name}】至其正前方！`);
                await moveOrPushUnitToSlot(item.zone, item.idx, oppFrontZone, targetCol);
              }
            }
          } else {
            const oppTributeFree = [];
            for (const oz of oppZones) {
              field[oz].forEach((u, idx) => {
                if (u && u.card && getCardTributeCost(u.card) === 0) {
                  oppTributeFree.push({ zone: oz, idx, unit: u });
                }
              });
            }
            if (oppTributeFree.length > 0) {
              const item = oppTributeFree[Math.floor(Math.random() * oppTributeFree.length)];
              logBattle(`✨ 對手 紅衣女孩 效果：拉動我方的【${item.unit.card.name}】至其正前方！`);
              await moveOrPushUnitToSlot(item.zone, item.idx, oppFrontZone, targetCol);
            }
          }
        }

        // (f-2) 人臉魚: 破壞我方場上1個單位
        if (unit.card.id === "R-VLG-0036" || unit.card.name.includes("人臉魚")) {
          const isPlayer = t.zone.startsWith("player_");
          const sideZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
          const sideOwner = isPlayer ? "player" : "enemy";
          
          if (isPlayer) {
            const myOtherUnits = [];
            for (const sz of sideZones) {
              field[sz].forEach((u, idx) => {
                if (u && (sz !== t.zone || idx !== t.idx)) {
                  myOtherUnits.push({ zone: sz, idx, name: u.card.name });
                }
              });
            }
            if (myOtherUnits.length > 0) {
              const choices = myOtherUnits.map((item, idx) => ({ text: `${item.name} (${item.zone.includes("front") ? "前" : "後"}${item.idx + 1})`, value: idx }));
              const chosenVal = await showXLWChoiceModal("人臉魚 效果發動", "獻祭人臉魚必須破壞我方場上一個其他單位：", choices);
              if (chosenVal !== null && chosenVal !== undefined) {
                const item = myOtherUnits[chosenVal];
                logBattle(`💥 人臉魚 效果：破壞了我方的【${item.name}】！`);
                await destroyUnit(item.zone, item.idx, sideOwner, false);
              }
            }
          } else {
            const oppOtherUnits = [];
            for (const sz of sideZones) {
              field[sz].forEach((u, idx) => {
                if (u && (sz !== t.zone || idx !== t.idx)) {
                  oppOtherUnits.push({ zone: sz, idx, unit: u });
                }
              });
            }
            if (oppOtherUnits.length > 0) {
              const item = oppOtherUnits[Math.floor(Math.random() * oppOtherUnits.length)];
              logBattle(`💥 對手 人臉魚 效果：破壞了對手的【${item.unit.card.name}】！`);
              await destroyUnit(item.zone, item.idx, sideOwner, false);
            }
          }
        }

        // (f-3) 地下怪鳥: 回收前方1個無須祭品的敵方單位
        if (unit.card.id === "R-VLG-0037" || unit.card.id === "R-VLG-0037-2025黑暗市集" || unit.card.name.includes("地下怪鳥")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
          const targetCol = t.idx;
          const oppUnit = field[oppFrontZone][targetCol];
          if (oppUnit && oppUnit.card && getCardTributeCost(oppUnit.card) === 0 && !(oppUnit.card.id === "NEU-0010" || oppUnit.card.id === "TOKEN_TRAVELER" || oppUnit.card.name?.includes("小旅人"))) {
            const oppHand = isPlayer ? (window.XLW_ENEMY.hand || []) : hand;
            oppHand.push(oppUnit.card);
            field[oppFrontZone][targetCol] = null;
            logBattle(`✨ 地下怪鳥 效果：將位於其前方的敵方單位【${oppUnit.card.name}】回收至其手牌！`);
            render();
          }
        }

        // (f-4) 製風龜龜: 推擠敵方前排戰線1個單位左或右
        if (unit.card.id === "R-VLG-0040" || unit.card.name.includes("製風龜龜")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
          const oppUnits = [];
          field[oppFrontZone].forEach((u, idx) => {
            if (u) oppUnits.push({ idx, name: u.card.name, unit: u });
          });
          
          if (oppUnits.length > 0) {
            if (isPlayer) {
              const choices = oppUnits.map((item, idx) => ({ text: `${item.name} (前排${item.idx + 1})`, value: idx }));
              const chosenVal = await showXLWChoiceModal("製風龜龜 效果發動", "選擇一個要推擠 of 敵方前排單位：", choices);
              if (chosenVal !== null && chosenVal !== undefined) {
                const item = oppUnits[chosenVal];
                const dirChoices = [{ text: "向左推擠", value: -1 }, { text: "向右推擠", value: 1 }];
                const chosenDir = await showXLWChoiceModal("製風龜龜 推擠方向", "請選擇推擠的方向：", dirChoices);
                if (chosenDir !== null && chosenDir !== undefined) {
                  const targetIdx = item.idx + chosenDir;
                  logBattle(`✨ 製風龜龜 效果：將對手【${item.name}】向${chosenDir === -1 ? "左" : "右"}推擠！`);
                  if (targetIdx < 0 || targetIdx > 4) {
                    logBattle(`💥 ${item.name} 被推到場外，直接進入墓地！`);
                    await destroyUnit(oppFrontZone, item.idx, "enemy", false);
                  } else {
                    await moveOrPushUnitToSlot(oppFrontZone, item.idx, oppFrontZone, targetIdx);
                  }
                }
              }
            } else {
              const item = oppUnits[Math.floor(Math.random() * oppUnits.length)];
              const pushDir = Math.random() < 0.5 ? -1 : 1;
              const targetIdx = item.idx + pushDir;
              logBattle(`✨ 對手 製風龜龜 效果：將我方【${item.name}】向${pushDir === -1 ? "左" : "右"}推擠！`);
              if (targetIdx < 0 || targetIdx > 4) {
                logBattle(`💥 ${item.name} 被推到場外，直接進入墓地！`);
                await destroyUnit(oppFrontZone, item.idx, "player", false);
              } else {
                await moveOrPushUnitToSlot(oppFrontZone, item.idx, oppFrontZone, targetIdx);
              }
            }
          }
        }

        // (f-5) 魔神仔: 將敵方後排所有單位向前推擠
        if (unit.card.id === "R-VLG-0055" || unit.card.name.includes("魔神仔")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppFrontZone = isPlayer ? "enemy_front" : "player_front";
          const oppBackZone = isPlayer ? "enemy_back" : "player_back";
          
          logBattle(`✨ 魔神仔 效果：推擠對手後排所有單位向前排！`);
          for (let i = 0; i < 5; i++) {
            if (field[oppBackZone][i]) {
              await moveOrPushUnitToSlot(oppBackZone, i, oppFrontZone, i);
            }
          }
        }

        // (f-6) 魔貨車: 破壞2個2星或以下單位
        if (unit.card.id === "SR-VLG-0029" || unit.card.name.includes("魔貨車")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
          const oppOwner = isPlayer ? "enemy" : "player";
          const eligible = [];
          for (const oz of oppZones) {
            field[oz].forEach((u, idx) => {
              if (u && u.card && Number(u.card.score || 0) <= 2) {
                eligible.push({ zone: oz, idx, name: u.card.name, unit: u });
              }
            });
          }
          
          if (eligible.length > 0) {
            window.XLW_currentEffectSourceUnit = unit;
            if (isPlayer) {
              let count = 0;
              while (count < 2 && eligible.length > 0) {
                const choices = eligible.map((item, idx) => ({ text: `${item.name} (${item.zone.includes("front") ? "前" : "後"}${item.idx + 1})`, value: idx }));
                choices.push({ text: "結束選擇", value: -1 });
                const chosen = await showXLWChoiceModal(`魔貨車 效果發動 (${count + 1}/2)`, "請選擇一個要破壞的 2 星或以下敵方單位：", choices);
                if (chosen === null || chosen === undefined || chosen === -1) {
                  break;
                }
                const item = eligible.splice(chosen, 1)[0];
                logBattle(`💥 魔貨車 效果：破壞了對手的【${item.name}】！`);
                await destroyUnit(item.zone, item.idx, "enemy", false);
                count++;
              }
            } else {
              const limit = Math.min(2, eligible.length);
              for (let i = 0; i < limit; i++) {
                const item = eligible[Math.floor(Math.random() * eligible.length)];
                eligible.splice(eligible.indexOf(item), 1);
                logBattle(`💥 對手 魔貨車 效果：破壞了我方的【${item.name}】！`);
                await destroyUnit(item.zone, item.idx, "player", false);
              }
            }
            window.XLW_currentEffectSourceUnit = null;
          }
        }

        // (f-7) 無臉人: 使本回合戰術佈陣可使用祭品召喚
        if (unit.card.id === "SR-VLG-0039" || unit.card.name.includes("無臉人")) {
          const isPlayer = t.zone.startsWith("player_");
          if (isPlayer) {
            window.XLW_playerFacelessManActive = true;
            logBattle("✨ 無臉人 效果：本回合我方在戰術佈陣階段打出的單位可為需要祭品的單位！");
          } else {
            window.XLW_enemyFacelessManActive = true;
            logBattle("✨ 對手 無臉人 效果：本回合對手在戰術佈陣階段打出的單位可為需要祭品的單位！");
          }
        }

        // (f-8) 毛線女孩: 獲得等同敵方場上受到禁錮單位數量的獎勵點數
        if (unit.card.id === "R-VLG-0044" || unit.card.id === "SSR-VLG-0044" || unit.card.id === "SSR-VLG-0044-金" || unit.card.name.includes("毛線女孩")) {
          const isPlayer = t.zone.startsWith("player_");
          const oppZones = isPlayer ? ["enemy_front", "enemy_back"] : ["player_front", "player_back"];
          let confinedCount = 0;
          for (const oz of oppZones) {
            field[oz].forEach((u, i) => {
              if (u && isUnitConfined(oz, i)) {
                confinedCount++;
              }
            });
          }
          if (confinedCount > 0) {
            if (isPlayer) {
              playerBonusScore += confinedCount;
              logBattle(`✨ 毛線女孩 效果：我方額外獲得 +${confinedCount}★ 獎勵點數！`);
              renderScore();
            } else {
              enemyBonusScore += confinedCount;
              logBattle(`✨ 對手 毛線女孩 效果：對手額外獲得 +${confinedCount}★ 獎勵點數！`);
              renderScore();
            }
          }
        }

        // (f-9) 紅眼小僧: 查看敵方牌庫頂3張牌，選1放底，其餘任意順序放回頂
        if (unit.card.id === "R-VLG-0050" || unit.card.name.includes("紅眼小僧")) {
          const isPlayer = t.zone.startsWith("player_");
          const targetDeck = isPlayer ? (window.XLW_ENEMY.deck || []) : deck;
          
          if (targetDeck.length > 0) {
            const topCards = targetDeck.slice(-3);
            targetDeck.splice(targetDeck.length - topCards.length, topCards.length);
            
            if (isPlayer) {
              const choices = topCards.map((c, i) => ({ text: c.name, value: i }));
              const chosenBottomIdx = await showXLWChoiceModal("紅眼小僧 效果發動：請選擇 1 張置於牌組底部", "置於底部的卡牌：", choices);
              let bottomIdx = (chosenBottomIdx !== null && chosenBottomIdx !== undefined) ? parseInt(chosenBottomIdx, 10) : 0;
              const bottomCard = topCards.splice(bottomIdx, 1)[0];
              targetDeck.unshift(bottomCard);
              
              logBattle(`✨ 紅眼小僧 效果：將對手牌組頂部的【${bottomCard.name}】移至牌組底部！`);
              
              if (topCards.length > 0) {
                const remaining = [...topCards];
                const ordered = [];
                while (remaining.length > 0) {
                  const remChoices = remaining.map((c, i) => ({ text: c.name, value: i }));
                  const chosenTopIdx = await showXLWChoiceModal("選擇最先放回牌組頂的卡牌 (越晚放回的越在最上面)", "置於頂端的卡牌：", remChoices);
                  let topIdx = (chosenTopIdx !== null && chosenTopIdx !== undefined) ? parseInt(chosenTopIdx, 10) : 0;
                  ordered.push(remaining.splice(topIdx, 1)[0]);
                }
                for (const c of ordered) {
                  targetDeck.push(c);
                }
                logBattle(`✨ 紅眼小僧 效果：已重新排列對手剩餘牌組頂部的卡牌。`);
              }
            } else {
              const bottomCard = topCards.splice(Math.floor(Math.random() * topCards.length), 1)[0];
              targetDeck.unshift(bottomCard);
              logBattle(`✨ 對手 紅眼小僧 效果：將我方牌組頂部的【${bottomCard.name}】移至牌組底部！`);
              topCards.sort(() => Math.random() - 0.5);
              topCards.forEach(c => targetDeck.push(c));
            }
          }
        }

        // (f-10) 如月站長: 使如月車站下方所有單位被召喚，並使車站進入墓地
        if (unit.card.id === "R-VLG-0031" || unit.card.name.includes("如月站長")) {
          const isPlayer = t.zone.startsWith("player_");
          const sideZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
          const sideOwner = isPlayer ? "player" : "enemy";
          
          let stationUnit = null;
          let stationZone = null;
          let stationIdx = -1;
          for (const sz of sideZones) {
            field[sz].forEach((u, idx) => {
              if (u && u.card && (u.card.id === "R-VLG-0018" || u.card.name.includes("如月車站"))) {
                stationUnit = u;
                stationZone = sz;
                stationIdx = idx;
              }
            });
          }
          
          if (stationUnit && stationUnit.storedUnits && stationUnit.storedUnits.length > 0) {
            logBattle(`✨ 如月站長 效果：開啟【如月車站】的封印，召喚其下方儲存的所有單位！`);
            const stored = stationUnit.storedUnits;
            stationUnit.storedUnits = [];
            
            const emptySlots = [];
            for (const sz of sideZones) {
              field[sz].forEach((u, i) => { if (!u) emptySlots.push({ zone: sz, idx: i }); });
            }
            
            for (const sc of stored) {
              if (emptySlots.length > 0) {
                const slot = emptySlots.shift();
                field[slot.zone][slot.idx] = {
                  card: sc,
                  tapped: false,
                  attacking: false,
                  target: null,
                  summonedTurn: turn,
                  summonedZone: slot.zone
                };
                logBattle(`✨ 召喚了儲存的單位【${sc.name}】！`);
              } else {
                logBattle(`場地已滿，【${sc.name}】無法被召喚而消失！`);
              }
            }
            
            logBattle(`💥 如月車站 已被關閉送入墓地！`);
            await destroyUnit(stationZone, stationIdx, sideOwner, false);
          }
        }
"""
if target_tribute_loop_start in code:
    code = code.replace(target_tribute_loop_start, target_tribute_loop_start + tribute_effects_body, 1)
    print("Success: Added tribute effects to executeTributeEffects loop.")
else:
    print("Error: executeTributeEffects loop start target not found!")
    sys.exit(1)

# 8. Add active skills for 如月車站, 百變喵, 肥宅喵 to renderField clicked handler (10 spaces indentation match)
target_active_skills_start = '          if ((phase === "召喚階段" || phase === "戰術佈陣") && zone.startsWith("player_")) {'
active_skills_body = """
            // (a-1) 如月車站 R-VLG-0018 (主動封存效果)
            if (obj.card.id === "R-VLG-0018" || obj.card.name?.includes("如月車站")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.stationUsedTurn === turn) {
                setStatus("如月車站 的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              const otherUnits = [];
              for (const z of ["player_front", "player_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u !== obj) otherUnits.push({ zone: z, idx: i, unit: u });
                });
              }
              if (otherUnits.length === 0) {
                setStatus("我方場上沒有其他單位可以放入車站封存！");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmUse = await showXLWConfirm("如月車站 效果發動", "是否選擇場上一個單位放置於車站下方進行封存？");
              if (confirmUse) {
                const choices = otherUnits.map((u, i) => ({ text: `${u.zone.includes("front") ? "前" : "後"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                const chosenIdx = await showXLWChoiceModal("選擇封存單位", "請選擇一個我方單位：", choices);
                if (chosenIdx !== null && chosenIdx !== undefined) {
                  const targetUnit = otherUnits[chosenIdx];
                  obj.storedUnits = obj.storedUnits || [];
                  obj.storedUnits.push(targetUnit.unit.card);
                  field[targetUnit.zone][targetUnit.idx] = null;
                  obj.stationUsedTurn = turn;
                  logBattle(`✨ 如月車站 效果：將我方場上的【${targetUnit.unit.card.name}】放入車站下方封存！`);
                  render();
                }
              }
              return;
            }

            // (a-2) 百變喵 SR-CAT-0034 (主動偷襲連動效果)
            if (obj.card.id === "SR-CAT-0034" || obj.card.name?.includes("百變喵")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.mimeMeowUsedTurn === turn) {
                setStatus("百變喵 的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              const sneakCats = [];
              for (const z of ["player_front", "player_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u !== obj && (u.card.deck === "喵喵賊" || u.card.faction === "喵喵賊" || u.card.id?.includes("CAT") || u.card.id?.includes("cat")) && window.xlwUnitHasSneak(u, z)) {
                    sneakCats.push({ zone: z, idx: i, unit: u });
                  }
                });
              }
              if (sneakCats.length === 0) {
                setStatus("場上沒有其他具備「偷襲」特性的喵喵賊單位！");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmUse = await showXLWConfirm("百變喵 效果發動", "是否選擇我方一個具備偷襲的喵喵賊單位，發動其偷襲成功效果，並將其與百變喵一同回收至手牌？");
              if (confirmUse) {
                const choices = sneakCats.map((u, i) => ({ text: `${u.zone.includes("front") ? "前" : "後"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                const chosenIdx = await showXLWChoiceModal("選擇偷襲單位百變", "請選擇喵喵賊偷襲單位：", choices);
                if (chosenIdx !== null && chosenIdx !== undefined) {
                  const targetUnit = sneakCats[chosenIdx];
                  obj.mimeMeowUsedTurn = turn;
                  logBattle(`✨ 百變喵 效果：準備發動【${targetUnit.unit.card.name}】的偷襲成功連動！`);
                  await triggerSneakAttackSuccessEffects(targetUnit.unit.card);
                  
                  // Return both to hand
                  field[zone][idx] = null;
                  field[targetUnit.zone][targetUnit.idx] = null;
                  hand.push(obj.card);
                  hand.push(targetUnit.unit.card);
                  logBattle(`✨ 百變喵 效果：將【百變喵】與【${targetUnit.unit.card.name}】回收至我方手牌！`);
                  render();
                }
              }
              return;
            }

            // (a-3) 肥宅喵 R-CAT-0029 (主動橫置得獎勵效果)
            if (obj.card.id === "R-CAT-0029" || obj.card.name?.includes("肥宅喵")) {
              if (window.isUnitSilenced(obj, zone, idx)) {
                setStatus("該單位處於沉默狀態，無法發動效果。");
                showModal(obj.card, obj.equipments);
                return;
              }
              if (obj.fatMeowUsedTurn === turn) {
                setStatus("肥宅喵 的效果本回合已使用過。");
                showModal(obj.card, obj.equipments);
                return;
              }
              const untappedCats = [];
              for (const z of ["player_front", "player_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u !== obj && !u.tapped && (u.card.deck === "喵喵賊" || u.card.faction === "喵喵賊" || u.card.id?.includes("CAT") || u.card.id?.includes("cat"))) {
                    untappedCats.push({ zone: z, idx: i, unit: u });
                  }
                });
              }
              if (untappedCats.length < 2) {
                setStatus("我方場上沒有至少 2 個其他未橫置的喵喵賊單位！");
                showModal(obj.card, obj.equipments);
                return;
              }
              const confirmUse = await showXLWConfirm("肥宅喵 效果發動", "是否選擇 2 個未橫置的喵喵賊單位橫置，以獲得 +1★ 獎勵點數？");
              if (confirmUse) {
                const choices1 = untappedCats.map((u, i) => ({ text: `${u.zone.includes("front") ? "前" : "後"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                const chosen1Idx = await showXLWChoiceModal("選擇第一個橫置喵單位", "請選擇：", choices1);
                if (chosen1Idx !== null && chosen1Idx !== undefined) {
                  const cat1 = untappedCats[chosen1Idx];
                  untappedCats.splice(chosen1Idx, 1);
                  
                  const choices2 = untappedCats.map((u, i) => ({ text: `${u.zone.includes("front") ? "前" : "後"}${u.idx + 1} 的 ${u.unit.card.name}`, value: i }));
                  const chosen2Idx = await showXLWChoiceModal("選擇第二個橫置喵單位", "請選擇：", choices2);
                  if (chosen2Idx !== null && chosen2Idx !== undefined) {
                    const cat2 = untappedCats[chosen2Idx];
                    
                    cat1.unit.tapped = true;
                    cat2.unit.tapped = true;
                    playerBonusScore += 1;
                    obj.fatMeowUsedTurn = turn;
                    logBattle(`✨ 肥宅喵 效果：橫置我方【${cat1.unit.card.name}】與【${cat2.unit.card.name}】，我方額外獲得 +1★ 獎勵！`);
                    renderScore();
                    render();
                  }
                }
              }
              return;
            }
"""
if target_active_skills_start in code:
    code = code.replace(target_active_skills_start, target_active_skills_start + active_skills_body, 1)
    print("Success: Added active skills clicked handlers to renderField.")
else:
    print("Error: renderField active skills click target not found!")
    sys.exit(1)

# 8b. Add window.XLW_currentEffectSourceUnit tracker for active skills (with 20 spaces indentation match)
# VRT-0025 (無頭副院長) player side
target_vdirector_play = """                    logBattle(`✨ 無頭副院長 效果：破壞對手的【${targetOpp.unit.card.name}】！`);
                    await destroyUnit(targetOpp.zone, targetOpp.idx, "enemy", false);"""
replacement_vdirector_play = """                    logBattle(`✨ 無頭副院長 效果：破壞對手的【${targetOpp.unit.card.name}】！`);
                    window.XLW_currentEffectSourceUnit = obj;
                    await destroyUnit(targetOpp.zone, targetOpp.idx, "enemy", false);
                    window.XLW_currentEffectSourceUnit = null;"""
if target_vdirector_play in code:
    code = code.replace(target_vdirector_play, replacement_vdirector_play, 1)
    print("Success: Added effect source tracker to player 無頭副院長.")
else:
    print("Error: player 無頭副院長 target not found!")
    sys.exit(1)

# VRT-0025 (無頭副院長) AI side (with 14 spaces indentation match)
target_vdirector_ai = """              logBattle(`✨ 對手 無頭副院長 效果：破壞我方的【${targetPlayer.unit.card.name}】！`);
              await destroyUnit(targetPlayer.zone, targetPlayer.idx, "player", false);"""
replacement_vdirector_ai = """              logBattle(`✨ 對手 無頭副院長 效果：破壞我方的【${targetPlayer.unit.card.name}】！`);
              window.XLW_currentEffectSourceUnit = item.unit;
              await destroyUnit(targetPlayer.zone, targetPlayer.idx, "player", false);
              window.XLW_currentEffectSourceUnit = null;"""
if target_vdirector_ai in code:
    code = code.replace(target_vdirector_ai, replacement_vdirector_ai, 1)
    print("Success: Added effect source tracker to AI 無頭副院長.")
else:
    print("Error: AI 無頭副院長 target not found!")
    sys.exit(1)

# 9. Add spell cases in castSpell()
target_spell_sunny = 'else if (card.name.includes("天氣晴") || card.id === "R-NMG-0021" || card.id === "SSSR-NMG-0021") {'
spell_cases_body = """else if (card.id === "R-VLG-0020" || card.name.includes("詛咒通靈")) {
    window.XLW_playerCurseSummonActive = true;
    logBattle("✨ 詛咒通靈 效果發動：我方下一次打出的單位可為需要祭品的單位！");
  }
  else if (card.id === "SR-VLG-0047" || card.name.includes("如月車票")) {
    const yokaiInHand = hand.filter(c => c && c.type === "unit" && getCardTributeCost(c) === 0 && (c.faction === "妖怪村莊" || c.id?.includes("VLG")));
    const choices = [
      { text: "【檢索】從牌庫尋找 [如月車站] 加入手牌", value: "search" }
    ];
    if (yokaiInHand.length > 0) {
      choices.push({ text: "【送墓】使手牌 1 張無須祭品的妖怪村莊單位送墓", value: "discard" });
    }
    
    const chosen = await showXLWChoiceModal("如月車票 選擇效果", "請選擇要執行的效果：", choices);
    if (chosen === "search") {
      const stationIdx = deck.findIndex(c => c && (c.id === "R-VLG-0018" || c.name.includes("如月車站")));
      if (stationIdx >= 0) {
        const stationCard = deck.splice(stationIdx, 1)[0];
        hand.push(stationCard);
        logBattle("✨ 如月車票 效果：將牌組中的【如月車站】加入手牌！");
        shuffle(deck);
      } else {
        logBattle("✨ 如月車票 效果：牌組中無【如月車站】。");
      }
    } else if (chosen === "discard") {
      const discardChoices = yokaiInHand.map((c, i) => ({ text: c.name, value: i }));
      const chosenDiscardIdx = await showXLWChoiceModal("選擇送墓的妖怪村莊單位", "請選擇：", discardChoices);
      if (chosenDiscardIdx !== null && chosenDiscardIdx !== undefined) {
        const discardedCard = yokaiInHand[chosenDiscardIdx];
        hand.splice(hand.indexOf(discardedCard), 1);
        graveyard.push(discardedCard);
        logBattle(`✨ 如月車票 效果：將手牌中的【${discardedCard.name}】送入墓地！`);
      }
    }
  }
  else if (card.id === "R-CAT-0019" || card.name.includes("逃脫")) {
    window.XLW_playerCatEscapeTurn = turn;
    logBattle("✨ 逃脫 效果發動：本次進攻時，我方所有被破壞的單位將回到手牌！");
  }
  else if (card.id === "R-VLG-0054" || card.name.includes("事故物件")) {
    const enemyUnits = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && !isUnitEffectImmune(u, z, i)) {
          enemyUnits.push({ zone: z, idx: i, name: u.card.name });
        }
      });
    }
    if (enemyUnits.length === 0) {
      setStatus("對手場上沒有可選擇的單位！");
      return;
    }
    const choices = enemyUnits.map((item, idx) => ({ text: `${item.name} (${item.zone.includes("front") ? "前" : "後"}${item.idx + 1})`, value: idx }));
    const chosenVal = await showXLWChoiceModal("事故物件 施加效果", "請選擇一個敵方單位：", choices);
    if (chosenVal !== null && chosenVal !== undefined) {
      const target = enemyUnits[chosenVal];
      const unit = field[target.zone][target.idx];
      unit.equipments = unit.equipments || [];
      unit.equipments.push("事故物件");
      unit.accidentProperty = true;
      logBattle(`✨ 事故物件 效果：使對手【${unit.card.name}】獲得「事故物件」詛咒效果！`);
    }
  }
  """
if target_spell_sunny in code:
    code = code.replace(target_spell_sunny, spell_cases_body + target_spell_sunny, 1)
    print("Success: Added spell cases in castSpell().")
else:
    print("Error: castSpell sunny target not found!")
    sys.exit(1)

# 10. Clear turn-based variables in endPlayerTurnAndRunEnemy
target_end_turn = "async function endPlayerTurnAndRunEnemy() {"
replacement_end_turn = """async function endPlayerTurnAndRunEnemy() {
  window.XLW_playerCurseSummonActive = false;
  window.XLW_playerFacelessManActive = false;
  window.XLW_enemyFacelessManActive = false;
  window.XLW_rainbowAtkBonusActive = false;"""
if target_end_turn in code:
    code = code.replace(target_end_turn, replacement_end_turn, 1)
    print("Success: Updated endPlayerTurnAndRunEnemy turn clear.")
else:
    print("Error: endPlayerTurnAndRunEnemy start target not found!")
    sys.exit(1)

# 11. Add Grass Meow (草叢喵) and Demon Lucky Cat (惡魔招財喵) turn start triggers
target_turn_draw = "async function performPlayerTurnStartDraw() {"
replacement_turn_draw = """async function performPlayerTurnStartDraw() {
  // 草叢喵 墓地回牌組效果
  const catIndex = graveyard.findIndex(c => c && (c.id === "R-CAT-0027" || c.name.includes("草叢喵")));
  if (catIndex >= 0 && deck.length > 0) {
    const catCard = graveyard.splice(catIndex, 1)[0];
    deck.push(catCard);
    shuffle(deck);
    logBattle("✨ 草叢喵 效果：主要階段開始時，將墓地中的【草叢喵】洗回牌庫！");
  }

  // 惡魔招財喵 墓地回手牌效果
  const demonIdx = graveyard.findIndex(c => c && (c.id === "SR-CAT-0026" || c.name.includes("惡魔招財喵")));
  if (demonIdx >= 0) {
    const demonCard = graveyard.splice(demonIdx, 1)[0];
    hand.push(demonCard);
    logBattle("✨ 惡魔招財喵 效果：主要階段開始時，將墓地中的【惡魔招財喵】回收至手牌！");
  }"""
if target_turn_draw in code:
    code = code.replace(target_turn_draw, target_turn_draw + "\n" + replacement_turn_draw, 1)
    print("Success: Added player turn-start graveyard triggers.")
else:
    print("Error: performPlayerTurnStartDraw target not found!")
    sys.exit(1)

# 12. Summon limits for 惡魔招財喵 (SR-CAT-0026) in canSummonCard
target_cansummon = "function canSummonCard(card, isPlayer) {"
replacement_cansummon = """function canSummonCard(card, isPlayer) {
  if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {
    const graveList = isPlayer ? graveyard : window.XLW_ENEMY.grave;
    const catCount = graveList.filter(c => c && (c.deck === "喵喵賊" || c.faction === "喵喵賊" || c.id?.includes("CAT") || c.id?.includes("cat"))).length;
    const ok = catCount >= 3;
    if (!ok && isPlayer) {
      setStatus("【召喚限制】惡魔招財喵 需要我方墓地有 3 個 or 以上的喵喵賊卡牌！");
    }
    return ok;
  }"""
if target_cansummon in code:
    code = code.replace(target_cansummon, target_cansummon + "\n" + replacement_cansummon, 1)
    print("Success: Added 惡魔招財喵 summon limit to canSummonCard.")
else:
    print("Error: canSummonCard start target not found!")
    sys.exit(1)

# 13. Scary Clown (恐怖小丑) trigger when entering player tactical phase
target_clown_tactical = 'if (phase === "戰術佈陣") {'
replacement_clown_tactical = """if (phase === "戰術佈陣") {
    // 恐怖小丑 (R-VLG-0048) 效果
    const clownIdx = graveyard.findIndex(c => c && (c.id === "R-VLG-0048" || c.name.includes("恐怖小丑")));
    const myUnits = [];
    for (const z of ["player_front", "player_back"]) {
      field[z].forEach((u, i) => { if (u) myUnits.push({ zone: z, idx: i, unit: u }); });
    }
    if (clownIdx >= 0 && myUnits.length === 1) {
      const confirm = await showXLWConfirm("恐怖小丑 效果發動", "偵測到墓地中有【恐怖小丑】且我方場上只有 1 個單位！是否獻祭該單位（觸發 2 次其被獻祭效果）並從墓地特殊召喚恐怖小丑？");
      if (confirm) {
        const targetUnit = myUnits[0];
        logBattle(`✨ 恐怖小丑 效果：獻祭場上唯一的單位 ${targetUnit.unit.card.name}，並額外發動 2 次其被獻祭效果！`);
        
        const dummyTributes = [{ zone: targetUnit.zone, idx: targetUnit.idx, key: `clown_tribute_${Date.now()}` }];
        const oldSelectedTributes = selectedTributes;
        selectedTributes = dummyTributes;
        
        await executeTributeEffects();
        await executeTributeEffects();
        
        await window.xlwPlayerTributeUnit(targetUnit.unit, targetUnit.zone, targetUnit.idx);
        field[targetUnit.zone][targetUnit.idx] = null;
        selectedTributes = oldSelectedTributes;
        
        const clownCard = graveyard.splice(clownIdx, 1)[0];
        field[targetUnit.zone][targetUnit.idx] = {
          card: clownCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: targetUnit.zone
        };
        logBattle(`✨ 恐怖小丑 已從墓地特殊召喚到 ${targetUnit.zone.includes("front") ? "前排" : "後排"}${targetUnit.idx + 1}！`);
        render();
      }
    }"""
if target_clown_tactical in code:
    code = code.replace(target_clown_tactical, target_clown_tactical + "\n" + replacement_clown_tactical, 1)
    print("Success: Added player Scary Clown trigger in changeActionPhase.")
else:
    print("Error: changeActionPhase tactical check target not found!")
    sys.exit(1)

# 14. Broken Mech Cat (壞掉的機械喵) sneak passive buff check in window.xlwUnitHasSneak
target_mech_cat_sneak = "const hasBaseSneak ="
replacement_mech_cat_sneak = """// 壞掉 of 機械喵 左右鄰居偷襲加成
  const isTraveler = card.id === "NEU-0010" || card.id === "TOKEN_TRAVELER" || card.name?.includes("小旅人") || card.name?.includes("旅人");
  if (!isTraveler && zone && field[zone]) {
    const idx = field[zone].indexOf(unit);
    if (idx >= 0) {
      const leftNeighbor = idx > 0 ? field[zone][idx - 1] : null;
      const rightNeighbor = idx < 4 ? field[zone][idx + 1] : null;
      const hasMechCat = (leftNeighbor && leftNeighbor.card && (leftNeighbor.card.id === "R-CAT-0025" || leftNeighbor.card.name?.includes("壞掉的機械喵")) && !window.isUnitSilenced(leftNeighbor, zone, idx - 1)) ||
                         (rightNeighbor && rightNeighbor.card && (rightNeighbor.card.id === "R-CAT-0025" || rightNeighbor.card.name?.includes("壞掉的機械喵")) && !window.isUnitSilenced(rightNeighbor, zone, idx + 1));
      if (hasMechCat) return true;
    }
  }

  const hasBaseSneak ="""
if target_mech_cat_sneak in code:
    code = code.replace(target_mech_cat_sneak, replacement_mech_cat_sneak, 1)
    print("Success: Updated xlwUnitHasSneak for Broken Mech Cat.")
else:
    print("Error: xlwUnitHasSneak target not found!")
    sys.exit(1)

# 15. Rainbow Cat attack bonus check in getUnitAtk
target_getatk_start = "function getUnitAtk(unit, zone, lane, isBeingAttacked = false) {\n  if (!unit) return 0;"
replacement_getatk_start = """function getUnitAtk(unit, zone, lane, isBeingAttacked = false) {
  if (!unit) return 0;
  let rainbowBonus = 0;
  if (window.XLW_rainbowAtkBonusActive && unit.attacking) {
    rainbowBonus = 1;
  }"""
target_getatk_return = """  // 迴旋飛斧 (最終攻擊力兩倍計算)
  if (unit.equipments && (unit.equipments.includes("迴旋飛斧") || unit.equipments.some(e => e.includes("迴旋飛斧")))) {
    baseAtk = baseAtk * 2;
  }

  return baseAtk;
}"""
replacement_getatk_return = """  // 迴旋飛斧 (最終攻擊力兩倍計算)
  if (unit.equipments && (unit.equipments.includes("迴旋飛斧") || unit.equipments.some(e => e.includes("迴旋飛斧")))) {
    baseAtk = baseAtk * 2;
  }

  return baseAtk + rainbowBonus;
}"""
if target_getatk_start in code and target_getatk_return in code:
    code = code.replace(target_getatk_start, replacement_getatk_start, 1)
    code = code.replace(target_getatk_return, replacement_getatk_return, 1)
    print("Success: Added Rainbow Cat attack bonus to getUnitAtk.")
else:
    print("Error: getUnitAtk targets not found!")
    sys.exit(1)

# 16. Kaka Small Giant (卡卡小巨人) check in runNeutralEndPhaseEffects
target_endphase_aunt = "// 1. 觀光阿姨 (NEU-0004 / R-NEU-0004)"
replacement_endphase_giant = """// 卡卡小巨人 (R-VLG-0041) 結束階段復活檢測
  if (isPlayerSide) {
    const myCount = field["player_front"].concat(field["player_back"]).filter(u => u !== null).length;
    const oppCount = field["enemy_front"].concat(field["enemy_back"]).filter(u => u !== null).length;
    const yokaiInGrave = graveyard.filter(c => c && (c.faction === "妖怪村莊" || c.id?.includes("VLG")));
    const giantIdx = graveyard.findIndex(c => c && (c.id === "R-VLG-0041" || c.name.includes("卡卡小巨人")));
    if (oppCount > myCount && yokaiInGrave.length >= 6 && giantIdx >= 0) {
      const emptySlots = [];
      for (const z of ["player_front", "player_back"]) {
        field[z].forEach((u, i) => { if (!u) emptySlots.push({ zone: z, idx: i }); });
      }
      if (emptySlots.length > 0) {
        const slot = emptySlots[0];
        const giantCard = graveyard.splice(giantIdx, 1)[0];
        field[slot.zone][slot.idx] = {
          card: giantCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: slot.zone
        };
        logBattle("✨ 卡卡小巨人 效果：我方場上單位較少且墓地妖怪卡達 6 張以上，卡卡小巨人自墓地特殊召喚！");
        render();
      }
    }
  } else {
    const myCount = field["player_front"].concat(field["player_back"]).filter(u => u !== null).length;
    const oppCount = field["enemy_front"].concat(field["enemy_back"]).filter(u => u !== null).length;
    const oppGrave = window.XLW_ENEMY.grave || [];
    const yokaiInGrave = oppGrave.filter(c => c && (c.faction === "妖怪村莊" || c.id?.includes("VLG")));
    const giantIdx = oppGrave.findIndex(c => c && (c.id === "R-VLG-0041" || c.name.includes("卡卡小巨人")));
    if (myCount > oppCount && yokaiInGrave.length >= 6 && giantIdx >= 0) {
      const emptySlots = [];
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => { if (!u) emptySlots.push({ zone: z, idx: i }); });
      }
      if (emptySlots.length > 0) {
        const slot = emptySlots[0];
        const giantCard = oppGrave.splice(giantIdx, 1)[0];
        field[slot.zone][slot.idx] = {
          card: giantCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: slot.zone
        };
        logBattle("✨ 對手 卡卡小巨人 效果：對手場上單位較少且墓地妖怪卡達 6 張以上，卡卡小巨人自墓地特殊召喚！");
        render();
      }
    }
  }

  // 1. 觀光阿姨 (NEU-0004 / R-NEU-0004)"""
if target_endphase_aunt in code:
    code = code.replace(target_endphase_aunt, replacement_endphase_giant, 1)
    print("Success: Added Kaka Small Giant to runNeutralEndPhaseEffects.")
else:
    print("Error: runNeutralEndPhaseEffects aunt target not found!")
    sys.exit(1)

# 17. AI regular summon destination logic for enemy summon cards (starting from line 12838)
target_ai_regular_sum = """    if (summonHandIdx >= 0 && (emptyFrontIdx >= 0 || emptyBackIdx >= 0)) {
      const card = window.XLW_ENEMY.hand[summonHandIdx];
      window.XLW_ENEMY.hand.splice(summonHandIdx, 1);
      
      const destZone = emptyFrontIdx >= 0 ? "enemy_front" : "enemy_back";
      const destIdx = emptyFrontIdx >= 0 ? emptyFrontIdx : emptyBackIdx;
      
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
      logBattle(`對手召喚：${card.name} 到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);"""

replacement_ai_regular_sum = """    let aiCanSummon = false;
    let destZone = null;
    let destIdx = -1;
    let card = null;

    if (summonHandIdx >= 0) {
      card = window.XLW_ENEMY.hand[summonHandIdx];
      
      // 惡魔招財喵 (SR-CAT-0026) AI 手牌限制檢查
      let okToSummon = true;
      if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {
        const oppGrave = window.XLW_ENEMY.grave || [];
        const catCount = oppGrave.filter(c => c && (c.deck === "喵喵賊" || c.faction === "喵喵賊" || c.id?.includes("CAT") || c.id?.includes("cat"))).length;
        if (catCount < 3) okToSummon = false;
      }
      
      if (okToSummon) {
        const canSummonToEnemy = xlwIsEnemySummonCard(card);
        if (canSummonToEnemy) {
          const playerFrontEmpty = field.player_front.findIndex(u => !u);
          const playerBackEmpty = field.player_back.findIndex(u => !u);
          if (playerFrontEmpty >= 0 || playerBackEmpty >= 0) {
            if (card.id === "R-VLG-0046" || card.name?.includes("背後靈")) {
              destZone = playerBackEmpty >= 0 ? "player_back" : "player_front";
              destIdx = playerBackEmpty >= 0 ? playerBackEmpty : playerFrontEmpty;
            } else {
              destZone = playerFrontEmpty >= 0 ? "player_front" : "player_back";
              destIdx = playerFrontEmpty >= 0 ? playerFrontEmpty : playerBackEmpty;
            }
          }
        } else if (emptyFrontIdx >= 0 || emptyBackIdx >= 0) {
          destZone = emptyFrontIdx >= 0 ? "enemy_front" : "enemy_back";
          destIdx = emptyFrontIdx >= 0 ? emptyFrontIdx : emptyBackIdx;
        }
        if (destZone && destIdx !== -1) {
          aiCanSummon = true;
        }
      }
    }

    if (aiCanSummon) {
      window.XLW_ENEMY.hand.splice(summonHandIdx, 1);
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
      logBattle(`對手召喚：${card.name} 到${destZone.startsWith("player_") ? "我方" : "對手"}${destZone === "player_front" || destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);"""
if target_ai_regular_sum in code:
    code = code.replace(target_ai_regular_sum, replacement_ai_regular_sum, 1)
    print("Success: Updated AI regular summon destination logic.")
else:
    print("Error: AI regular summon target block not found!")
    sys.exit(1)

# 18. AI tactical phase Scary Clown (恐怖小丑) check
target_ai_tactical = '      if (opponentAttackCount === 0) {\n        phase = "\\u6230\\u8853\\u4f48\\u9663";'
replacement_ai_tactical = """      if (opponentAttackCount === 0) {
        phase = "\\u6230\\u8853\\u4f48\\u9663";
        
        // AI 恐怖小丑 (R-VLG-0048) 效果發動
        const enemyGrave = window.XLW_ENEMY.grave || [];
        const clownIdx = enemyGrave.findIndex(c => c && (c.id === "R-VLG-0048" || c.name.includes("恐怖小丑")));
        const enemyUnits = [];
        for (const z of ["enemy_front", "enemy_back"]) {
          field[z].forEach((u, i) => { if (u) enemyUnits.push({ zone: z, idx: i, unit: u }); });
        }
        if (clownIdx >= 0 && enemyUnits.length === 1) {
          const targetUnit = enemyUnits[0];
          logBattle(`✨ 對手 恐怖小丑 效果：對手獻祭其場上唯一的單位 ${targetUnit.unit.card.name}，並額外發動 2 次其被獻祭效果！`);
          
          const dummyTributes = [{ zone: targetUnit.zone, idx: targetUnit.idx, key: `clown_tribute_enemy_${Date.now()}` }];
          const oldSelectedTributes = selectedTributes;
          selectedTributes = dummyTributes;
          
          await executeTributeEffects();
          await executeTributeEffects();
          
          await window.xlwEnemyTributeUnit(targetUnit.unit, targetUnit.zone, targetUnit.idx);
          field[targetUnit.zone][targetUnit.idx] = null;
          selectedTributes = oldSelectedTributes;
          
          const clownCard = enemyGrave.splice(clownIdx, 1)[0];
          field[targetUnit.zone][targetUnit.idx] = {
            card: clownCard,
            tapped: false,
            attacking: false,
            target: null,
            summonedTurn: turn,
            summonedZone: targetUnit.zone
          };
          logBattle(`✨ 對手 恐怖小丑 已從墓地特殊召喚到 ${targetUnit.zone.includes("front") ? "前排" : "後排"}${targetUnit.idx + 1}！`);
          render();
        }"""
if target_ai_tactical in code:
    code = code.replace(target_ai_tactical, replacement_ai_tactical, 1)
    print("Success: Updated AI Scary Clown trigger in runEnemyTurn.")
else:
    print("Error: AI Scary Clown trigger target not found!")
    sys.exit(1)

# 19. Insert AI active skills and spell casting logic into runEnemyTurn
target_ai_magic = "    // AI 召喚階段發動魔法卡\n    await aiPlayMagicCardsSummonPhase();"
replacement_ai_magic = """    // AI 召喚階段發動魔法卡
    await aiPlayMagicCardsSummonPhase();

    // AI 肥宅喵 (R-CAT-0029) 效果發動
    const aiFatMeows = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "R-CAT-0029" || u.card.name?.includes("肥宅喵"))) {
          if (!window.isUnitSilenced(u, z, i) && u.fatMeowUsedTurn !== turn) {
            aiFatMeows.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    }
    for (const fm of aiFatMeows) {
      const untappedCats = [];
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u !== fm.unit && !u.tapped && (u.card.deck === "喵喵賊" || u.card.faction === "喵喵賊" || u.card.id?.includes("CAT") || u.card.id?.includes("cat"))) {
            untappedCats.push(u);
          }
        });
      }
      if (untappedCats.length >= 2) {
        untappedCats[0].tapped = true;
        untappedCats[1].tapped = true;
        enemyBonusScore += 1;
        fm.unit.fatMeowUsedTurn = turn;
        logBattle(`✨ 對手 肥宅喵 效果：橫置對手【${untappedCats[0].card.name}】與【${untappedCats[1].card.name}】，對手額外獲得 +1★ 獎勵！`);
        renderScore();
        render();
      }
    }

    // AI 百變喵 (SR-CAT-0034) 效果發動
    const aiMimes = [];
    for (const z of ["enemy_front", "enemy_back"]) {
      field[z].forEach((u, i) => {
        if (u && u.card && (u.card.id === "SR-CAT-0034" || u.card.name?.includes("百變喵"))) {
          if (!window.isUnitSilenced(u, z, i) && u.mimeMeowUsedTurn !== turn) {
            aiMimes.push({ zone: z, idx: i, unit: u });
          }
        }
      });
    }
    for (const mime of aiMimes) {
      let target = null;
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u !== mime.unit && (u.card.deck === "喵喵賊" || u.card.faction === "喵喵賊" || u.card.id?.includes("CAT") || u.card.id?.includes("cat")) && window.xlwUnitHasSneak(u, z)) {
            target = { zone: z, idx: i, unit: u };
          }
        });
      }
      if (target) {
        mime.unit.mimeMeowUsedTurn = turn;
        logBattle(`✨ 對手 百變喵 效果：準備發動【${target.unit.card.name}】的偷襲成功連動！`);
        await triggerEnemySneakAttackSuccessEffects(target.unit.card);
        field[mime.zone][mime.idx] = null;
        field[target.zone][target.idx] = null;
        window.XLW_ENEMY.hand.push(mime.unit.card);
        window.XLW_ENEMY.hand.push(target.unit.card);
        logBattle(`✨ 對手 百變喵 效果：將【百變喵】與【${target.unit.card.name}】回收至對手手牌！`);
        render();
        await sleep(800);
      }
    }"""
if target_ai_magic in code:
    code = code.replace(target_ai_magic, replacement_ai_magic, 1)
    print("Success: Inserted AI active skills into runEnemyTurn.")
else:
    print("Error: AI active skills target in runEnemyTurn not found!")
    sys.exit(1)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)

print("All static/game_v8.js core changes applied successfully!")
