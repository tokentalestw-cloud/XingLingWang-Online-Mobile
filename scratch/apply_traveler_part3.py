import codecs

def inject_part3():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # handleSummon injections (SPT-0004, SPT-0015, SPT-0012)
    summon_effects_code = '''
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
              // AI auto combine
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
    if 'SPT-0004' not in content[content.find('if (card.id === "VRT-0009"'):content.find('if (card.id === "VRT-0009"')+2000]:
        content = content.replace('if (card.id === "VRT-0009" || card.name?.includes("打卡的酒醉鄉民")) {', summon_effects_code)


    # SPT-0009 (胖旅人) in destroyUnit
    destroy_code = '''// 特殊旅人預組 - SPT-0009 胖旅人 (被破壞時召喚 2 個小旅人)
if (unit.card && (unit.card.id === "SPT-0009" || unit.card.name?.includes("胖旅人"))) {
    const isPlayer = zone.startsWith("player_");
    logBattle(`✨ ${isPlayer ? "我方" : "對手"} 胖旅人 被破壞效果觸發：召喚 2 個小旅人！`);
    // 延遲觸發，避免破壞動畫衝突
    setTimeout(async () => {
        await promptAndSummonTraveler(isPlayer ? "player" : "enemy", 2, "胖旅人");
    }, 500);
}

// R-ORC-0023 阿姨獸人 敵方小旅人被擊破效果'''
    if 'SPT-0009' not in content[content.find('// R-ORC-0023'):content.find('// R-ORC-0023')+1000]:
        content = content.replace('// R-ORC-0023 阿姨獸人 敵方小旅人被擊破效果', destroy_code)


    # SPT-0006 (惡魔旅人) active skill
    active_skill_code = '''const isTicketCollector = obj.card?.id === "R-ART-0050" || obj.card?.name?.includes("博物館剪票員");

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
    
    // 如果有彈出視窗，這裡我們直接蓋過，避免 showModal 阻擋
    // We can prompt inside a timeout or immediately.
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
                // Find correct index in grave
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
    if 'SPT-0006' not in content[content.find('const isTicketCollector'):content.find('const isTicketCollector')+2000]:
        content = content.replace('const isTicketCollector = obj.card?.id === "R-ART-0050" || obj.card?.name?.includes("博物館剪票員");', active_skill_code)


    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected part 3 successfully.")

inject_part3()
