import codecs
import re

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Insert `isFairy` before `function getUnitStars`
if 'const isFairy =' not in text:
    fairy_def = '\nconst isFairy = (u) => u && u.card && (u.card.name?.includes("妖精") || u.card.faction === "妖精" || u.card.race === "妖精");\n\n'
    text = text.replace('function getUnitStars', fairy_def + 'function getUnitStars')

# 2. Inject into `getUnitStars`
stars_marker = '  // 衰退扣分'
stars_injection = """
  // 妖精預組計分效果
  const isBackRow = zone && zone.includes("_back");
  const isFrontRow = zone && zone.includes("_front");
  const prefix = zone ? (zone.startsWith("player_") ? "player_" : "enemy_") : "";
  
  if (c.id === "EVL-0007" || c.name?.includes("妖精女孩 小英")) {
    if (isBackRow) baseStars += 3;
  }
  
  if (c.id === "EVL-0010" || c.name?.includes("妖精司令 艾文")) {
    if (zone && field[zone]) {
      for (let k = 0; k < 5; k++) {
        if (k !== lane) {
          const other = field[zone][k];
          if (isFairy(other)) baseStars += 1;
        }
      }
    }
  }
  
  if (c.id === "EVL-0011" || c.name?.includes("風流妖精")) {
    if (zone && lane !== undefined) {
      const positions = [
        { z: zone, idx: lane - 1 },
        { z: zone, idx: lane + 1 },
        { z: isBackRow ? prefix + "front" : prefix + "back", idx: lane }
      ];
      for (const pos of positions) {
        if (pos.idx >= 0 && pos.idx < 5 && field[pos.z]) {
          const other = field[pos.z][pos.idx];
          if (isFairy(other) && !window.isUnitSilenced(other, pos.z, pos.idx)) baseStars += 1;
        }
      }
    }
  }
  
  // EVL-0003 盾牌妖精: 給後方單位+2星 (從後方單位的視角計算)
  if (isBackRow && lane !== undefined) {
    const frontUnit = field[prefix + "front"][lane];
    if (frontUnit && (frontUnit.card?.id === "EVL-0003" || frontUnit.card?.name?.includes("盾牌妖精")) && !window.isUnitSilenced(frontUnit, prefix + "front", lane)) {
      baseStars += 2;
    }
  }

"""
if 'EVL-0007' not in text:
    text = text.replace(stars_marker, stars_injection + stars_marker)

# 3. Inject into `getUnitAtk`
atk_marker = '  // 河童場地減攻效果'
atk_injection = """
  // 妖精預組攻擊力修改
  if (c.id === "R-EVL-0021" || c.name?.includes("壯壯妖精")) {
    const sidePrefix = zone && zone.startsWith("player_") ? "player_" : "enemy_";
    const frontZone = sidePrefix + "front";
    let fairyCount = 0;
    if (field[frontZone]) {
      field[frontZone].forEach(u => {
        if (isFairy(u)) fairyCount++;
      });
    }
    baseAtk += fairyCount;
  }

  if (zone && lane !== undefined && field[zone]) {
    const adjSpaces = [lane - 1, lane + 1];
    for (const idx of adjSpaces) {
      if (idx >= 0 && idx < 5) {
        const adj = field[zone][idx];
        if (adj && adj.card && (adj.card.id === "R-EVL-0006" || adj.card.name?.includes("妖精戰士長 葛登")) && !window.isUnitSilenced(adj, zone, idx)) {
          baseAtk += 2;
        }
      }
    }
  }

  if (zone && zone.includes("front")) {
    const oppPrefix = zone.startsWith("player_") ? "enemy_" : "player_";
    const oppFront = oppPrefix + "front";
    const oppBack = oppPrefix + "back";
    let hasJailer = false;
    for (const z of [oppFront, oppBack]) {
      if (field[z]) {
        field[z].forEach((u, i) => {
          if (u && u.card && (u.card.id === "R-EVL-0035" || u.card.name?.includes("黑妖精獄卒")) && !window.isUnitSilenced(u, z, i)) {
            hasJailer = true;
          }
        });
      }
    }
    if (hasJailer) baseAtk = Math.max(0, baseAtk - 1);
  }

"""
if 'R-EVL-0021' not in text:
    text = text.replace(atk_marker, atk_injection + atk_marker)

# 4. Inject into `isUnitMagicImmune`
immune_marker = '  // 中星城菁英 (R-NMS-0075 / SSSR-NMS-0075)'
immune_injection = """
  // 奇異妖精 (R-EVL-0012)
  if (isFairy(unit) && z && i !== undefined && i !== -1) {
    if (i > 0 && field[z][i-1] && (field[z][i-1].card?.id === "R-EVL-0012" || field[z][i-1].card?.name?.includes("奇異妖精")) && !window.isUnitSilenced(field[z][i-1], z, i-1)) return true;
    if (i < 4 && field[z][i+1] && (field[z][i+1].card?.id === "R-EVL-0012" || field[z][i+1].card?.name?.includes("奇異妖精")) && !window.isUnitSilenced(field[z][i+1], z, i+1)) return true;
  }

"""
if 'R-EVL-0012' not in text:
    text = text.replace(immune_marker, immune_injection + immune_marker)


# 5. Inject into `destroyUnit`
destroy_marker = '  if (isUnitIndestructible(unit, zone, idx, isCombatDestruction)) {'
destroy_injection = """
  // 守墓黑妖精 薩德 (R-EVL-0016)
  if (unit.card && (unit.card.id === "R-EVL-0016" || unit.card.name?.includes("守墓黑妖精")) && !window.isUnitSilenced(unit, zone, idx)) {
    const isPlayer = zone.startsWith("player_");
    const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY?.grave || []);
    const myHand = isPlayer ? hand : (window.XLW_ENEMY?.hand || []);
    const fairyInGrave = myGrave.filter(c => c && (c.name?.includes("妖精") || c.faction === "妖精" || c.race === "妖精"));
    if (fairyInGrave.length > 0) {
      if (isPlayer) {
        const choices = fairyInGrave.map((c, i) => ({ text: `${c.name}`, value: myGrave.indexOf(c) }));
        const chosen = await showXLWChoiceModal("守墓黑妖精 效果", "請選擇一張墓地的妖精單位回手牌：", choices);
        if (chosen !== null && chosen !== undefined) {
          const card = myGrave[chosen];
          myGrave.splice(chosen, 1);
          myHand.push(card);
          logBattle(`✨ 守墓黑妖精 效果發動：將墓地中的 ${card.name} 回收至手牌！`);
        }
      } else {
        const card = fairyInGrave[0];
        const graveIdx = myGrave.indexOf(card);
        myGrave.splice(graveIdx, 1);
        myHand.push(card);
        logBattle(`✨ 對手 守墓黑妖精 效果發動：回收了 ${card.name}！`);
      }
    }
  }

  // 妖精同胞情 (EVL-0019) Trap logic
  if (isFairy(unit)) {
    const isPlayer = zone.startsWith("player_");
    const myHand = isPlayer ? hand : (window.XLW_ENEMY?.hand || []);
    const myDeck = isPlayer ? deck : (window.XLW_ENEMY?.deck || []);
    const myGrave = isPlayer ? graveyard : (window.XLW_ENEMY?.grave || []);
    const trapIdx = myHand.findIndex(c => c && (c.id === "EVL-0019" || c.name?.includes("妖精同胞情")));
    if (trapIdx >= 0) {
      if (isPlayer) {
        const confirmTrap = await showXLWConfirm("妖精同胞情", `你的妖精單位即將被破壞，是否發動【妖精同胞情】？`);
        if (confirmTrap) {
          const trapCard = myHand[trapIdx];
          myHand.splice(trapIdx, 1);
          myGrave.push(trapCard);
          logBattle(`✨ 妖精同胞情 發動！`);
          const top2 = myDeck.splice(myDeck.length - 2, 2);
          if (top2.length > 0) {
            const fairies = top2.filter(c => c.name?.includes("妖精") || c.faction === "妖精" || c.race === "妖精");
            if (fairies.length > 0) {
              const choices = fairies.map((c, i) => ({ text: c.name, value: i }));
              const chosen = await showXLWChoiceModal("特召妖精", "請選擇要特殊召喚的妖精（取消則全部送墓）：", choices);
              if (chosen !== null && chosen !== undefined) {
                const target = fairies[chosen];
                await window.xlwSpecialSummonUnit(target, true);
                logBattle(`✨ 特召 ${target.name} 成功！`);
                top2.forEach((c, i) => { if (c !== target) myGrave.push(c); });
              } else {
                top2.forEach(c => myGrave.push(c));
              }
            } else {
              top2.forEach(c => myGrave.push(c));
              logBattle("牌庫頂2張沒有妖精單位，全部送入墓地。");
            }
          }
        }
      } else {
         const trapCard = myHand[trapIdx];
         myHand.splice(trapIdx, 1);
         myGrave.push(trapCard);
         logBattle(`✨ 對手發動 妖精同胞情！`);
         const top2 = myDeck.splice(myDeck.length - 2, 2);
         if (top2.length > 0) {
           const fairies = top2.filter(c => c.name?.includes("妖精") || c.faction === "妖精" || c.race === "妖精");
           if (fairies.length > 0) {
             const target = fairies[0];
             await window.xlwSpecialSummonUnit(target, false);
             logBattle(`✨ 對手特召了 ${target.name} 成功！`);
             top2.forEach(c => { if (c !== target) myGrave.push(c); });
           } else {
             top2.forEach(c => myGrave.push(c));
           }
         }
      }
    }
  }

"""
if 'R-EVL-0016' not in text:
    text = text.replace(destroy_marker, destroy_injection + destroy_marker)


# 6. Inject into `performSummonToSlot`
# Using regex to match the end of performSummonToSlot's try block precisely
summon_injection = """
        // 妖精女王 梅瑟琳 (EVL-0002)
        if (card.id === "EVL-0002" || card.name?.includes("妖精女王")) {
          const isPlayer = zone.startsWith("player_");
          const myHand = isPlayer ? hand : (window.XLW_ENEMY?.hand || []);
          if (isPlayer) {
            const unitChoices = myHand.map((c, i) => {
              if (c && (c.type === "unit" || c.type === "character") && getCardTributeCost(c) === 0) {
                return { text: c.name, value: i };
              }
              return null;
            }).filter(x => x !== null);
            if (unitChoices.length > 0) {
              const confirmQueen = await showXLWConfirm("妖精女王 特召", "是否從手牌額外打出 1 張無須祭品的單位？");
              if (confirmQueen) {
                const chosen = await showXLWChoiceModal("妖精女王 特召", "請選擇：", unitChoices);
                if (chosen !== null && chosen !== undefined) {
                  const targetCard = myHand[chosen];
                  myHand.splice(chosen, 1);
                  await window.xlwSpecialSummonUnit(targetCard, true);
                  logBattle(`✨ 妖精女王 特召了 ${targetCard.name}！`);
                }
              }
            }
          }
        }

        // 淨化老妖精 (EVL-0013)
        if (card.id === "EVL-0013" || card.name?.includes("淨化老妖精")) {
          const isPlayer = zone.startsWith("player_");
          if (isPlayer) {
            const confirmPurify = await showXLWConfirm("淨化老妖精 淨化", "是否選擇場上一單位，將其配戴的所有魔法卡/裝備送入墓地？");
            if (confirmPurify) {
              const validTargets = [];
              for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
                field[z].forEach((u, i) => {
                  if (u && u.equipments && u.equipments.length > 0) {
                    validTargets.push({ zone: z, idx: i, name: u.card.name, u: u });
                  }
                });
              }
              if (validTargets.length > 0) {
                const choices = validTargets.map((t, idx) => ({ text: `${t.name} (${t.zone.includes("player")?"我方":"對方"}${t.zone.includes("front")?"前排":"後排"}${t.idx+1})`, value: idx }));
                const chosen = await showXLWChoiceModal("選擇淨化目標", "請選擇要淨化的單位：", choices);
                if (chosen !== null && chosen !== undefined) {
                  const t = validTargets[chosen];
                  t.u.equipments = [];
                  if (t.u.effects) t.u.effects = [];
                  logBattle(`✨ 淨化老妖精 解除了 ${t.name} 身上的所有裝備與狀態！`);
                  render();
                }
              } else {
                alert("場上無身上配備魔法卡的單位。");
              }
            }
          }
        }

        // 妖精預言家 (EVL-0015)
        if (card.id === "EVL-0015" || card.name?.includes("妖精預言家")) {
          const isPlayer = zone.startsWith("player_");
          const myDeck = isPlayer ? deck : (window.XLW_ENEMY?.deck || []);
          if (myDeck.length >= 3 && isPlayer) {
            const confirmProphet = await showXLWConfirm("妖精預言家 占卜", "是否查看牌庫頂 3 張牌並調換順序？");
            if (confirmProphet) {
              const top3 = myDeck.splice(myDeck.length - 3, 3);
              const choices1 = top3.map((c, i) => ({ text: c.name, value: i }));
              const topChoice = await showXLWChoiceModal("選擇置於最頂端", "請選擇置於最頂端(馬上抽到)的卡片：", choices1);
              let topCard = top3[0], midCard = top3[1], botCard = top3[2];
              if (topChoice !== null && topChoice !== undefined) {
                topCard = top3.splice(topChoice, 1)[0];
                const choices2 = top3.map((c, i) => ({ text: c.name, value: i }));
                const midChoice = await showXLWChoiceModal("選擇置於第二張", "請選擇置於第二張的卡片：", choices2);
                if (midChoice !== null && midChoice !== undefined) {
                  midCard = top3.splice(midChoice, 1)[0];
                  botCard = top3[0];
                } else {
                  midCard = top3[0]; botCard = top3[1];
                }
                myDeck.push(botCard);
                myDeck.push(midCard);
                myDeck.push(topCard);
                logBattle(`✨ 妖精預言家 重新排列了牌庫頂的卡片。`);
              } else {
                myDeck.push(top3[0], top3[1], top3[2]); // return unchanged
              }
            }
          }
        }

"""

if 'EVL-0002' not in text:
    target_pattern = r'(\n    } catch \(err\) \{\n      logDebug\("\[召喚失敗\].*?"\);\n      if \(window\.XLW_reportError\))'
    m = re.search(target_pattern, text)
    if m:
        text = text[:m.start()] + '\n' + summon_injection + text[m.start():]
    else:
        print("Failed to find performSummonToSlot catch block anchor!")

with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replacement script generated and executed safely.")
