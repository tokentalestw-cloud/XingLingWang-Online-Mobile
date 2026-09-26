import codecs

def reinject_final_safe():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings to \n for robust replacing
    content = content.replace('\r\n', '\n')

    replacements = []

    # 1. promptAndSummonTraveler & SR-SPT-0029 (from inject_helper.py)
    helper_code = '''async function promptAndSummonTraveler(side, count, sourceName) {
    if (count <= 0) return;
    const isPlayer = side === "player";
    const frontZone = isPlayer ? "player_front" : "enemy_front";
    const backZone = isPlayer ? "player_back" : "enemy_back";

    // 檢查 SR-SPT-0029 (樹葉旅人) 效果：召喚小旅人時追加召喚 1 個
    let leafBonus = 0;
    const leafTrackerKey = isPlayer ? "XLW_playerLeafTravelerUsedThisTurn" : "XLW_enemyLeafTravelerUsedThisTurn";
    if (!window[leafTrackerKey]) {
        let hasLeaf = false;
        for (const z of [frontZone, backZone]) {
            field[z].forEach(u => {
                if (u && u.card && (u.card.id === "SR-SPT-0029" || u.card.name?.includes("樹葉旅人")) && !window.isUnitSilenced(u, z, field[z].indexOf(u))) {
                    hasLeaf = true;
                }
            });
        }
        if (hasLeaf) {
            window[leafTrackerKey] = true;
            leafBonus = 1;
            logBattle(`✨ ${isPlayer ? "我方" : "對手"} 樹葉旅人 效果發動：追加召喚 1 個小旅人！`);
        }
    }
    const totalToSummon = count + leafBonus;

    for (let c = 0; c < totalToSummon; c++) {
        const emptySlots = [];
        [frontZone, backZone].forEach(z => {
            field[z].forEach((u, i) => { if (!u) emptySlots.push({ zone: z, idx: i }); });
        });
        
        if (emptySlots.length === 0) {
            logBattle(`${isPlayer ? "我方" : "對手"} 場上已滿，無法召喚更多小旅人。`);
            break;
        }

        let chosenSlot = emptySlots[0];
        if (isPlayer) {
            const choices = emptySlots.map(s => ({
                text: `${s.zone.includes("front") ? "前排" : "後排"}${s.idx + 1}`,
                value: JSON.stringify(s)
            }));
            const res = await showXLWChoiceModal(`${sourceName} 效果`, `請選擇第 ${c + 1}/${totalToSummon} 個小旅人召喚的位置：`, choices);
            if (res !== null && res !== undefined) {
                chosenSlot = JSON.parse(choices[res].value);
            }
        }
        
        const travelerCard = allCards.find(c => c && (c.id === "TOKEN_TRAVELER" || c.name.includes("小旅人"))) 
            || { id: "TOKEN_TRAVELER", name: "小旅人", type: "unit", tribute: 0, attack: "1", score: 1 };
            
        field[chosenSlot.zone][chosenSlot.idx] = {
            card: JSON.parse(JSON.stringify(travelerCard)),
            tapped: false, attacking: false, target: null,
            summonedTurn: turn, summonedZone: chosenSlot.zone, equipments: []
        };
        logBattle(`召喚了一個【小旅人】至 ${chosenSlot.zone.includes("front") ? "前排" : "後排"}${chosenSlot.idx + 1}。`);
        if (typeof animateCardDrop === 'function') animateCardDrop(chosenSlot.zone, chosenSlot.idx);
    }
    render();
}

function processCombine'''
    
    replacements.append(("function processCombine", helper_code, "Helper Function"))

    # 2. SPT-0001
    spt_0001_code = '''  let baseAtkNum = parseInt(baseAtk, 10);
  if (isNaN(baseAtkNum)) baseAtkNum = 0;

  // 特殊旅人預組 - SPT-0001 金白蘭旅人 (每有1個其他旅人，攻擊力+1)
  if (c.id === "SPT-0001" || c.name?.includes("金白蘭旅人")) {
      let travelerCount = 0;
      const isPlayer = zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("旅人") || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      baseAtkNum += travelerCount;
  }
'''
    replacements.append((
        "  let baseAtkNum = parseInt(baseAtk, 10);\n  if (isNaN(baseAtkNum)) baseAtkNum = 0;",
        spt_0001_code,
        "SPT-0001 (getUnitAtk)"
    ))

    # 3. SPT-0016
    spt_0016_code = '''function getUnitStars(unit, zone, idx) {
  if (!unit || !unit.card) return 0;
  const c = unit.card;
  let s = parseInt(c.score, 10) || 0;
  
  // 特殊旅人預組 - SPT-0016 派對旅人 (每有1個其他小旅人，星數+1)
  if (c.id === "SPT-0016" || c.name?.includes("派對旅人")) {
      let travelerCount = 0;
      const isPlayer = zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== idx) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      s += travelerCount;
  }
'''
    replacements.append((
        "function getUnitStars(unit, zone, idx) {\n  if (!unit || !unit.card) return 0;\n  const c = unit.card;\n  let s = parseInt(c.score, 10) || 0;",
        spt_0016_code,
        "SPT-0016 (getUnitStars)"
    ))

    # 4. R-SPT-0008
    r_spt_0008_code = '''window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
const prefix = isPlayerSide ? "player_" : "enemy_";

// 特殊旅人預組 - R-SPT-0008 旅店常客 (主要階段開始，召喚 1 個小旅人)
for (const z of [prefix + "front", prefix + "back"]) {
  for (let i = 0; i < 5; i++) {
    const u = field[z][i];
    if (u && u.card && (u.card.id === "R-SPT-0008" || u.card.name?.includes("旅店常客")) && !window.isUnitSilenced(u, z, i)) {
      logBattle(`✨ ${isPlayerSide ? "我方" : "對手"} 旅店常客 效果觸發：主要階段開始，召喚 1 個小旅人！`);
      await promptAndSummonTraveler(isPlayerSide ? "player" : "enemy", 1, "旅店常客");
    }
  }
}
'''
    replacements.append((
        'window.xlwResolveTurnStartEffects = async function(isPlayerSide) {\nconst prefix = isPlayerSide ? "player_" : "enemy_";',
        r_spt_0008_code,
        "R-SPT-0008 (xlwResolveTurnStartEffects)"
    ))

    # 5. R-SPT-0014
    r_spt_0014_code = '''function isUnitMagicImmune(unit, zone, idx) {
  if (!unit || !unit.card) return false;
  const c = unit.card;
  
  // 特殊旅人預組 - R-SPT-0014 魔法旅人 (小旅人獲得魔法抗性)
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
    const side = zone.startsWith("player_") ? "player_" : "enemy_";
    const hasMagicTraveler = field[side + "front"].concat(field[side + "back"]).some(u => u && u.card && (u.card.id === "R-SPT-0014" || u.card.name?.includes("魔法旅人")) && !window.isUnitSilenced(u, side, field[side+"front"].includes(u)?field[side+"front"].indexOf(u):field[side+"back"].indexOf(u)));
    if (hasMagicTraveler) return true;
  }
'''
    replacements.append((
        "function isUnitMagicImmune(unit, zone, idx) {\n  if (!unit || !unit.card) return false;\n  const c = unit.card;",
        r_spt_0014_code,
        "R-SPT-0014 (isUnitMagicImmune)"
    ))

    # 6. SPT-0013
    spt_0013_code = '''  // 不可獻祭判定
  const c = unit.card || unit;
  
  // 特殊旅人預組 - SPT-0013 黃金旅人 獻祭限制
  const targetCardForTribute = window.playerHand[selectedHandForTribute];
  if (targetCardForTribute && (targetCardForTribute.id === "SPT-0013" || targetCardForTribute.name?.includes("黃金旅人"))) {
      if (!(c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人"))) {
          setStatus(`【獻祭失敗】黃金旅人的祭品必須是小旅人！`);
          return;
      }
  }
'''
    replacements.append((
        "  // 不可獻祭判定\n  const c = unit.card || unit;",
        spt_0013_code,
        "SPT-0013 (toggleTributeSelection)"
    ))

    # 7. SPT-0004, 0015, 0012
    summon_code = '''
  // 特殊旅人預組 - SPT-0004 機械旅人 (進場召喚1小旅人)
  if (card.id === "SPT-0004" || card.name?.includes("機械旅人")) {
      const isPlayer = zone.startsWith("player_");
      logBattle(`✨ ${isPlayer ? "我方" : "對手"} 機械旅人 效果觸發：進場時召喚 1 個小旅人！`);
      await promptAndSummonTraveler(isPlayer ? "player" : "enemy", 1, "機械旅人");
  }

  // 特殊旅人預組 - SPT-0015 討拍旅人 (進場破壞正前方所有敵方小旅人)
  if (card.id === "SPT-0015" || card.name?.includes("討拍旅人")) {
      const isPlayer = zone.startsWith("player_");
      const oppFront = isPlayer ? "enemy_front" : "player_front";
      const oppBack = isPlayer ? "enemy_back" : "player_back";
      let destroyedAny = false;
      for (const z of [oppFront, oppBack]) {
          const oppUnit = field[z][idx];
          if (oppUnit && oppUnit.card && (oppUnit.card.id === "TOKEN_TRAVELER" || oppUnit.card.name?.includes("小旅人"))) {
              logBattle(`✨ ${isPlayer ? "我方" : "對手"} 討拍旅人 效果觸發：破壞正前方的敵方小旅人【${oppUnit.card.name}】！`);
              await destroyUnit(z, idx, isPlayer ? "enemy" : "player", false, false);
              destroyedAny = true;
          }
      }
      if (destroyedAny) render();
  }

  // 特殊旅人預組 - SPT-0012 多頭機械旅人 (合體時召喚 2 個小旅人)
  if (card.id === "SPT-0012" || card.name?.includes("多頭機械旅人")) {
      const isPlayer = zone.startsWith("player_");
      const myZones = isPlayer ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
      let targets = [];
      myZones.forEach(z => {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== idx) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人") || u.card.name?.includes("旅人"))) {
                  targets.push({ zone: z, idx: i, name: u.card.name, u });
              }
          });
      });
      if (targets.length > 0) {
          if (isPlayer) {
              const choices = targets.map((t, i) => ({ text: `${t.name} (${t.zone.includes("front")?"前排":"後排"}${t.idx+1})`, value: i }));
              choices.push({ text: "不發動合體", value: -1 });
              const chosen = await showXLWChoiceModal("多頭機械旅人 合體效果", "請選擇我方一個旅人單位進行合體：", choices);
              if (chosen !== null && chosen !== -1) {
                  const target = targets[chosen];
                  logBattle(`✨ 多頭機械旅人 效果：與 【${target.name}】 進行合體，並額外召喚 2 個小旅人！`);
                  target.u.equipments = target.u.equipments || [];
                  target.u.equipments.push("多頭機械旅人 (合體)");
                  target.u.bonusScore = (target.u.bonusScore || 0) + 1; // 假設合體給予+1獎勵
                  field[zone][idx] = null; // 自己離場
                  await promptAndSummonTraveler("player", 2, "多頭機械旅人");
                  render();
              }
          } else {
              const target = targets[0];
              logBattle(`✨ 對手 多頭機械旅人 效果：與 【${target.name}】 進行合體，並額外召喚 2 個小旅人！`);
              target.u.equipments = target.u.equipments || [];
              target.u.equipments.push("多頭機械旅人 (合體)");
              target.u.bonusScore = (target.u.bonusScore || 0) + 1;
              field[zone][idx] = null;
              await promptAndSummonTraveler("enemy", 2, "多頭機械旅人");
              render();
          }
      }
  }

if (card.id === "VRT-0009" || card.name?.includes("打卡的酒醉鄉民")) {'''
    replacements.append((
        'if (card.id === "VRT-0009" || card.name?.includes("打卡的酒醉鄉民")) {',
        summon_code,
        "SPT-0004, 0015, 0012 (handleSummon)"
    ))

    # 8. SPT-0009
    destroy_code = '''// 特殊旅人預組 - SPT-0009 胖旅人 (被破壞時召喚 2 個小旅人)
if (unit.card && (unit.card.id === "SPT-0009" || unit.card.name?.includes("胖旅人"))) {
    const isPlayer = zone.startsWith("player_");
    logBattle(`✨ ${isPlayer ? "我方" : "對手"} 胖旅人 被破壞效果觸發：召喚 2 個小旅人！`);
    setTimeout(async () => {
        await promptAndSummonTraveler(isPlayer ? "player" : "enemy", 2, "胖旅人");
    }, 500);
}

// R-ORC-0023 阿姨獸人 敵方小旅人被擊破效果'''
    replacements.append((
        '// R-ORC-0023 阿姨獸人 敵方小旅人被擊破效果',
        destroy_code,
        "SPT-0009 (destroyUnit)"
    ))

    # 9. SPT-0006
    active_code = '''const isTicketCollector = obj.card?.id === "R-ART-0050" || obj.card?.name?.includes("博物館剪票員");

// 特殊旅人預組 - SPT-0006 惡魔旅人
if (obj.card?.id === "SPT-0006" || obj.card?.name?.includes("惡魔旅人")) {
    if (obj.tapped) {
        setStatus("【惡魔旅人】已橫置，無法發動效果！");
        return;
    }
    if (window.XLW_playerActionsPerformedThisTurn || obj.summonedTurn === turn) {
        setStatus("【惡魔旅人】在剛召喚的回合無法發動效果，下一回合才能使用！");
        showModal(obj.card, obj.equipments);
        return;
    }
    const myUnits = [];
    const zones = ["player_front", "player_back"];
    zones.forEach((z) => {
        field[z].forEach((u, i) => {
            if (u && u !== obj) myUnits.push({ zone: z, idx: i, name: u.card.name, u });
        });
    });
    if (myUnits.length < 2) {
        setStatus("【惡魔旅人】我方場上其他單位不足 2 個，無法發動效果！");
        showModal(obj.card, obj.equipments);
        return;
    }
    if (playerGrave.filter(c => c && c.type === "unit").length === 0) {
        setStatus("【惡魔旅人】墓地沒有單位可供特殊召喚！");
        showModal(obj.card, obj.equipments);
        return;
    }
    
    setTimeout(async () => {
        const confirmUse = await showXLWConfirm("惡魔旅人 效果", "是否發動【惡魔旅人】效果：橫置此單位，破壞我方 2 個其他單位，並從墓地特殊召喚 1 個單位？");
        if (confirmUse) {
            obj.tapped = true;
            let choices1 = myUnits.map((u, i) => ({ text: `${u.name} (${u.zone.includes("front")?"前排":"後排"}${u.idx+1})`, value: i }));
            let chosen1 = await showXLWChoiceModal("選擇第 1 個破壞單位", "請選擇：", choices1);
            if (chosen1 === null || chosen1 === undefined) { obj.tapped = false; return; }
            const target1 = myUnits[chosen1];
            myUnits.splice(chosen1, 1);
            
            let choices2 = myUnits.map((u, i) => ({ text: `${u.name} (${u.zone.includes("front")?"前排":"後排"}${u.idx+1})`, value: i }));
            let chosen2 = await showXLWChoiceModal("選擇第 2 個破壞單位", "請選擇：", choices2);
            if (chosen2 === null || chosen2 === undefined) { obj.tapped = false; return; }
            const target2 = myUnits[chosen2];
            
            await destroyUnit(target1.zone, target1.idx, "player", false, false);
            await destroyUnit(target2.zone, target2.idx, "player", false, false);
            
            const graveChoices = playerGrave.filter(c => c && c.type === "unit").map((c, i) => ({ text: c.name, value: i }));
            let chosenGrave = await showXLWChoiceModal("惡魔旅人 效果：從墓地特召", "請選擇要復活的單位：", graveChoices);
            if (chosenGrave !== null && chosenGrave !== undefined) {
                const unitCardsInGrave = playerGrave.map((c, idx) => ({ c, idx })).filter(item => item.c && item.c.type === "unit");
                const realGraveIdx = unitCardsInGrave[chosenGrave].idx;
                const revivedCard = playerGrave.splice(realGraveIdx, 1)[0];
                
                let emptySlot = null;
                for (let z of ["player_front", "player_back"]) {
                    const eIdx = field[z].findIndex(u => !u);
                    if (eIdx !== -1) { emptySlot = { zone: z, idx: eIdx }; break; }
                }
                if (emptySlot) {
                    field[emptySlot.zone][emptySlot.idx] = {
                        card: revivedCard, tapped: false, attacking: false, target: null,
                        summonedTurn: turn, summonedZone: emptySlot.zone, equipments: []
                    };
                    logBattle(`✨ 惡魔旅人 效果發動：橫置自身，破壞了 2 個單位，並從墓地特召了【${revivedCard.name}】！`);
                    if (typeof animateCardDrop === 'function') animateCardDrop(emptySlot.zone, emptySlot.idx);
                } else {
                    playerGrave.push(revivedCard);
                    logBattle("我方場上已滿，無法特召！");
                }
            }
            window.XLW_playerActionsPerformedThisTurn = true;
            render();
        }
    }, 100);
    return;
}
'''
    replacements.append((
        'const isTicketCollector = obj.card?.id === "R-ART-0050" || obj.card?.name?.includes("博物館剪票員");',
        active_code,
        "SPT-0006 (active skill)"
    ))

    # 10. SPT-0017
    spt_0017_code = '''} else if (card.id === "SPT-0017" || card.name?.includes("大大術")) {
      const targets = [];
      for (const z of ["player_front", "player_back"]) {
          field[z].forEach((u, i) => {
              if (u && u.card && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人"))) {
                  targets.push({ zone: z, idx: i, name: u.card.name, unit: u });
              }
          });
      }
      if (targets.length === 0) {
          setStatus("【大大術】我方場上沒有小旅人單位可供強化！");
          hand.splice(handIndex, 0, card);
          render();
          return;
      }
      const choices = targets.map((t, i) => ({ text: `${t.name} (${t.zone.includes("front")?"前排":"後排"}${t.idx+1})`, value: i }));
      const chosenIdx = await showXLWChoiceModal("大大術 效果發動", "請選擇我方一個小旅人賦予 +4 攻擊力：", choices);
      if (chosenIdx === null || chosenIdx === undefined) {
          hand.splice(handIndex, 0, card);
          render();
          return;
      }
      
      const targetItem = targets[chosenIdx];
      const spellCard = hand.splice(handIndex, 1)[0];
      await showSpellActivationOverlay(spellCard, "player");
      await castSpellChain(spellCard, async () => {
          targetItem.unit.atkModifier = (targetItem.unit.atkModifier || 0) + 4;
          logBattle(`✨ 大大術 效果：我方 ${targetItem.name} 獲得 +4 攻擊力！`);
          playerGrave.push(spellCard);
          render();
      });
} else if (card.id === "SR-FMS-0016" || card.name?.includes("大三元")) {'''
    replacements.append((
        '} else if (card.id === "SR-FMS-0016" || card.name?.includes("大三元")) {',
        spt_0017_code,
        "SPT-0017 (castSpell)"
    ))

    # 11. SPT-0018
    spt_0018_code = '''window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  // 特殊旅人預組 - SPT-0018 觀光樂園 (結束階段結束後召喚 3 個小旅人)
  const sidePrefix = isPlayerSide ? "player_" : "enemy_";
  for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
      for (let i = 0; i < 5; i++) {
          const u = field[z][i];
          if (u && u.card && (u.card.id === "SPT-0018" || u.card.name?.includes("觀光樂園")) && !window.isUnitSilenced(u, z, i)) {
              logBattle(`✨ ${isPlayerSide ? "我方" : "對手"} 觀光樂園 效果觸發：結束階段結束後召喚 3 個小旅人！`);
              await promptAndSummonTraveler(isPlayerSide ? "player" : "enemy", 3, "觀光樂園");
          }
      }
  }
'''
    replacements.append((
        'window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {',
        spt_0018_code,
        "SPT-0018 (xlwResolveEndPhaseEffects)"
    ))

    success = 0
    for old, new_c, name in replacements:
        if old in content:
            content = content.replace(old, new_c)
            print(f"[OK] {name} injected.")
            success += 1
        elif new_c in content:
            print(f"[ALREADY EXISTS] {name}")
            success += 1
        else:
            print(f"[FAILED] {name} - Anchor not found!")
            print(f"  Expected Anchor: {old[:50]}...")
            
    # Normalize line endings back to \r\n if needed, though browsers handle \n fine.
    # We will write it with \n for consistency to avoid mixed line endings.
    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Total injections: {success}/{len(replacements)}")

reinject_final_safe()
