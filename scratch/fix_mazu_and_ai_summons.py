# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    content = open(filepath, encoding="utf-8").read()
    content_norm = content.replace("\r\n", "\n")
    
    # 1. Add Mazu summon restriction check to canSummonCard
    target_cansummon = """  // R-FMS-0030 / SSR-FMS-0030 高塔101號 限制
  if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {"""

    replacement_cansummon = """  // SR-FMS-0036 麻祖 限制
  if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
    const exile = isPlayer ? playerExileZone : enemyExileZone;
    const hasHu = exile.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
    if (!hasHu) {
      if (isPlayer) {
        setStatus("【召喚限制】除外區沒有大三元或小四喜等胡牌，無法召喚麻祖！");
      }
      return false;
    }
  }

  // R-FMS-0030 / SSR-FMS-0030 高塔101號 限制
  if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {"""

    if target_cansummon in content_norm:
        content_norm = content_norm.replace(target_cansummon, replacement_cansummon)
        print("Successfully added Mazu check to canSummonCard.")
    else:
        print("Warning: target_cansummon not found!")

    # 2. Append Happy Island AI summon effects to triggerAiSummonEffects
    target_ai_effects = """    } else {
      logBattle("對手 驅魔人 效果：場上沒有附加任何裝備卡/魔法卡的單位。");
    }
  }
}"""

    replacement_ai_effects = """    } else {
      logBattle("對手 驅魔人 效果：場上沒有附加 any 裝備卡/魔法卡的單位。");
    }
  }

  // ===== 歡樂島 AI/Sync 立即召喚效果 =====
  const isPlayer = destZone.startsWith("player_");
  
  // R-FMS-0007 大腸包小腸
  if (card.id === "R-FMS-0007" || card.name?.includes("大腸包小腸")) {
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
            await kidnapCard(t.zone, t.idx, destZone, destIdx);
            render();
          }
        } else {
          const t = targets[Math.floor(Math.random() * targets.length)];
          await kidnapCard(t.zone, t.idx, destZone, destIdx);
          render();
        }
      }
    }
  }
  // R-FMS-0009 / R-FMS-0010 / R-FMS-0011 紅中哥/白板哥/發財哥
  else if (card.name?.includes("紅中哥") || card.name?.includes("白板哥") || card.name?.includes("發財哥")) {
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
  else if (card.id === "R-FMS-0013" || card.name?.includes("北小妹")) {
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
  else if (card.id === "R-FMS-0014" || card.name?.includes("西小弟")) {
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
  else if (card.id === "R-FMS-0015" || card.name?.includes("南大姊")) {
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
  else if (card.name?.includes("西南季風")) {
    const oppFront = isPlayer ? "enemy_front" : "player_front";
    const oppBack = isPlayer ? "enemy_back" : "player_back";
    const oppHand = isPlayer ? (window.XLW_ENEMY.hand || []) : hand;
    
    let targetUnit = field[oppFront][destIdx];
    if (targetUnit) {
      const existingBack = field[oppBack][destIdx];
      if (existingBack) {
        logBattle(`💥 【${existingBack.card.name}】被推擠出戰線，返回其手牌！`);
        oppHand.push(existingBack.card);
      }
      field[oppBack][destIdx] = targetUnit;
      targetUnit.summonedZone = oppBack;
      field[oppFront][destIdx] = null;
      logBattle(`✨ 西南季風 效果：推擠對手【${targetUnit.card.name}】至後排！`);
      render();
    } else {
      targetUnit = field[oppBack][destIdx];
      if (targetUnit) {
        logBattle(`💥 【${targetUnit.card.name}】被推擠出戰線，返回其手牌！`);
        oppHand.push(targetUnit.card);
        field[oppBack][destIdx] = null;
        render();
      }
    }
  }
  // SR-FMS-0020 東北季風
  else if (card.name?.includes("東北季風")) {
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
  else if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
    if (isPlayer) {
      const confirm101 = await showXLWConfirm("高塔101號 效果發動", "是否展示任意張手牌以觸發被展示效果？");
      if (confirm101) {
        const choices = hand.map((c, i) => ({ text: `${c.name}`, value: i }));
        const chosen = await showXLWChoiceModal("選擇要展示的手牌", "請選擇任意卡牌展示（可多選/單選）：", choices);
        if (chosen !== null && chosen !== undefined) {
          await window.xlwRevealCard(hand[chosen], true);
        }
      }
    } else {
      const oppHand = window.XLW_ENEMY.hand || [];
      for (const c of oppHand) {
        if (c) await window.xlwRevealCard(c, false);
      }
    }
  }
  // R-FMS-0031 詐胡牌
  else if (card.id === "R-FMS-0031" || card.name?.includes("詐胡牌")) {
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
  else if (card.id === "R-FMS-0032" || card.name?.includes("好大雞牌")) {
    const myHand = isPlayer ? hand : (window.XLW_ENEMY.hand || []);
    if (isPlayer) {
      const confirmChicken = await showXLWConfirm("好大雞牌 效果發動", "展示 2 張手牌（確定）還是展示牌庫頂 2 張卡牌（取消）？");
      if (confirmChicken) {
        if (myHand.length >= 2) {
          await window.xlwRevealCard(myHand[0], true);
          await window.xlwRevealCard(myHand[1], true);
        } else if (myHand.length > 0) {
          await window.xlwRevealCard(myHand[0], true);
        }
      } else {
        await window.xlwRevealTopCards(2, true);
      }
    } else {
      if (Math.random() < 0.5 && myHand.length >= 2) {
        await window.xlwRevealCard(myHand[0], false);
        await window.xlwRevealCard(myHand[1], false);
      } else {
        await window.xlwRevealTopCards(2, false);
      }
    }
  }
  // SR-FMS-0036 麻祖
  else if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
    const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY.grave || []);
    const myDeck = isPlayer ? deck : (window.XLW_ENEMY.deck || []);
    
    const graveMahjongs = myGrave.filter(c => c && window.isMahjongUnit(c));
    const fieldMahjongs = [];
    const sidePrefix = isPlayer ? "player_" : "enemy_";
    [sidePrefix + "front", sidePrefix + "back"].forEach(z => {
      field[z].forEach((u, i) => {
        if (u && u !== field[destZone][destIdx] && u.card && window.isMahjongUnit(u.card)) {
          fieldMahjongs.push({ zone: z, idx: i, card: u.card });
        }
      });
    });
    
    if (isPlayer) {
      const confirmMazu = await showXLWConfirm("麻祖 效果發動", "是否發動【麻祖】效果，將我方場上與墓地任意數量的其他麻將單位洗回牌庫並連續召喚？");
      if (confirmMazu) {
        let washCount = 0;
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
}"""

    # We only want to keep the magic cards: 西南季風 (R-FMS-0021) and 東北季風 (SR-FMS-0020) inside castSpell!
    replacement_cast_dead = """  } else if (card.id === "R-FMS-0021" || card.name?.includes("西南季風") || card.name?.includes("東北季風")) {
    await performSummonToSlot(card, handIndex);"""

    # Target 3: Clean up redundant unit checks inside castSpell (lines 2837 to 2865 in the reconstructed file)
    # The reconstruction has these lines. Let's find them.
    target_cast_dead = """  } else if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
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
  } else if (card.id === "R-FMS-0001" || card.id === "R-FMS-0002" || card.id === "R-FMS-0005" || card.id === "R-FMS-0003" || card.id === "R-FMS-0012" || card.id === "R-FMS-0024" || card.id === "R-FMS-0029" || card.id === "R-FMS-0026" || card.id === "R-FMS-0027" || card.id === "SR-FMS-0004" || card.id === "SR-FMS-0025" || card.id === "SR-FMS-0028" || card.id === "R-FMS-0033" || card.id === "SR-FMS-0020") {
    await performSummonToSlot(card, handIndex);"""

    if target_cansummon in content_norm:
        content_norm = content_norm.replace(target_cansummon, replacement_cansummon)
        print("Successfully added Mazu check to canSummonCard.")
    else:
        print("Warning: target_cansummon not found!")

    if target_ai_effects in content_norm:
        content_norm = content_norm.replace(target_ai_effects, replacement_ai_effects)
        print("Successfully added Happy Island AI effects to triggerAiSummonEffects.")
    else:
        print("Warning: target_ai_effects not found!")

    if target_cast_dead in content_norm:
        content_norm = content_norm.replace(target_cast_dead, replacement_cast_dead)
        print("Successfully removed dead unit checks from castSpell.")
    else:
        print("Warning: target_cast_dead not found!")

    open(filepath, "w", encoding="utf-8").write(content_norm)
    print("Mazu and AI summon fixes applied successfully.")

if __name__ == '__main__':
    main()
