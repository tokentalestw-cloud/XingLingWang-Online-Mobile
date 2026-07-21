import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

# Define the targets and replacements
replacements = [
    # 1. Helper functions
    (
        """function draw(n) {
  const deckName = $("deckSelect") ? $("deckSelect").value : "喵喵賊";
  for (let i = 0; i < n; i++) {
    if (deck.length === 0) {
      setStatus("牌庫已空。");
      break;
    }
    const c = deck.pop();
    if (c) {
      hand.push(c);
    }
  }
}""",
        """function draw(n) {
  const deckName = $("deckSelect") ? $("deckSelect").value : "喵喵賊";
  for (let i = 0; i < n; i++) {
    if (deck.length === 0) {
      setStatus("牌庫已空。");
      break;
    }
    const c = deck.pop();
    if (c) {
      hand.push(c);
    }
  }
}

// 智慧的般若/憤怒的般若：視覺化展示抽到的卡牌
function showRevealedCardModal(card, ownerName) {
  const overlay = document.createElement("div");
  overlay.className = "xlw-modal-overlay";
  overlay.style = "position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;";
  
  const box = document.createElement("div");
  box.style = "background: #1a1a2e; color: #fff; padding: 25px; border-radius: 12px; border: 2px solid #e94560; max-width: 320px; text-align: center; box-shadow: 0 0 20px rgba(233, 69, 96, 0.5); font-family: sans-serif;";
  
  const title = document.createElement("h3");
  title.style = "margin-top: 0; color: #e94560; font-size: 18px;";
  title.textContent = `智慧的般若 展示卡牌 (${ownerName})`;
  
  const cardEl = document.createElement("div");
  cardEl.style = "margin: 20px auto; width: 140px; height: 196px; border: 1px solid #444; border-radius: 8px; overflow: hidden; position: relative; background: #111;";
  if (card.image) {
    cardEl.innerHTML = `<img src="${card.image}" style="width:100%; height:100%; object-fit:cover;">`;
  } else {
    cardEl.innerHTML = `<div style="padding: 20px; font-size: 12px; color: #aaa;">${card.name}</div>`;
  }
  
  const text = document.createElement("div");
  text.style = "font-size: 14px; margin-bottom: 20px;";
  text.textContent = `對手展示了抽到的卡牌：【${card.name}】`;
  
  const btn = document.createElement("button");
  btn.style = "background: #e94560; color: #fff; border: none; padding: 8px 20px; border-radius: 6px; cursor: pointer; font-weight: bold;";
  btn.textContent = "確認";
  btn.onclick = () => overlay.remove();
  
  box.appendChild(title);
  box.appendChild(cardEl);
  box.appendChild(text);
  box.appendChild(btn);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
}

// 智慧的般若/憤怒的般若：我方回合開始抽牌異步處理
async function performPlayerTurnStartDraw() {
  const drawn = [];
  for (let i = 0; i < 2; i++) {
    if (deck.length > 0) {
      drawn.push(deck.pop());
    }
  }
  
  if (drawn.length === 0) {
    setStatus("牌庫已空。");
    render();
    return;
  }
  
  const oppHasSmartPrajna = field["enemy_front"].concat(field["enemy_back"]).some(u => u && u.card && u.card.name.includes("智慧的般若"));
  const oppHasAngryPrajna = field["enemy_front"].concat(field["enemy_back"]).some(u => u && u.card && u.card.name.includes("憤怒的般若"));
  
  if (oppHasAngryPrajna) {
    // 憤怒的般若：我方選擇1張除外
    let exiledCard = null;
    let keepCards = [];
    if (drawn.length === 1) {
      exiledCard = drawn[0];
    } else {
      const choices = drawn.map((c, idx) => ({ text: `${c.name} (${c.type === "unit" ? "單位" : "魔法"})`, value: idx }));
      const chosenIdxVal = await showXLWChoiceModal("憤怒的般若：選擇除外的卡牌", "對手場上有【憤怒的般若】，請選擇一張你抽到的卡牌進行除外：", choices);
      const chosenIdx = (chosenIdxVal !== null && chosenIdxVal !== undefined) ? parseInt(chosenIdxVal, 10) : 0;
      exiledCard = drawn[chosenIdx];
      keepCards = drawn.filter((_, idx) => idx !== chosenIdx);
    }
    
    playerExileZone.push(exiledCard);
    keepCards.forEach(c => hand.push(c));
    logBattle(`憤怒的般若 效果：我方選擇將抽出的卡片 ${exiledCard.name} 除外！`);
    
    if (isMultiplayer) {
      ws.send(JSON.stringify({
        action: "hannya_exile_drawn_card",
        exiledCard: exiledCard,
        drawnCount: drawn.length
      }));
    }
  } else if (oppHasSmartPrajna) {
    // 智慧的般若：我方選擇1張展示
    let revealedCard = null;
    if (drawn.length === 1) {
      revealedCard = drawn[0];
    } else {
      const choices = drawn.map((c, idx) => ({ text: `${c.name} (${c.type === "unit" ? "單位" : "魔法"})`, value: idx }));
      const chosenIdxVal = await showXLWChoiceModal("智慧的般若：選擇展示的卡牌", "對手場上有【智慧的般若】，請選擇一張你抽到的卡牌展示給對手：", choices);
      const chosenIdx = (chosenIdxVal !== null && chosenIdxVal !== undefined) ? parseInt(chosenIdxVal, 10) : 0;
      revealedCard = drawn[chosenIdx];
    }
    
    drawn.forEach(c => hand.push(c));
    logBattle(`智慧的般若 效果：我方選擇展示抽出的卡片：【${revealedCard.name}】！`);
    
    if (isMultiplayer) {
      ws.send(JSON.stringify({
        action: "hannya_reveal_drawn_card",
        revealedCard: revealedCard,
        drawnCount: drawn.length
      }));
    } else {
      // 單人模式 (AI對手)
      // 若展示的是單位卡，且AI有憤怒的般若與智慧的般若，AI會自動升級進化
      if (revealedCard.type === "unit" || revealedCard.type === "單位") {
        const hannyaSlots = [];
        for (const zone of ["enemy_front", "enemy_back"]) {
          field[zone].forEach((u, idx) => {
            if (u && u.card && u.card.name.includes("智慧的般若")) {
              hannyaSlots.push({ zone, idx, unit: u });
            }
          });
        }
        
        const angryCard = enemyExtraDeck.find(c => c && (c.id === "SR-VLG-0049" || c.name.includes("憤怒的般若")));
        if (hannyaSlots.length > 0 && angryCard) {
          const { zone, idx, unit } = hannyaSlots[0];
          window.XLW_ENEMY.grave.push(unit.card);
          enemyGraveyard = window.XLW_ENEMY.grave;
          enemyExtraDeck.splice(enemyExtraDeck.indexOf(angryCard), 1);
          field[zone][idx] = {
            card: structuredClone(angryCard),
            tapped: false,
            attacking: false,
            target: null,
            summonedTurn: turn,
            summonedZone: zone
          };
          logBattle(`✨ 對手 額外進化：對手場上的【智慧的般若】已升級進化為【憤怒的般若】！`);
          playerBonusScore = Math.max(0, playerBonusScore - 1);
        }
      }
    }
  } else {
    // 正常抽牌
    drawn.forEach(c => hand.push(c));
  }
  
  render();
}"""
    ),
    # 2. AI draw block in runEnemyTurn
    (
        """    // 2. 對手抽 2 張
    let drawn = 0;
    const hasSmartPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name.includes("智慧的般若"));
    const hasAngryPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name.includes("憤怒的般若"));

    for (let i = 0; i < 2; i++) {
      if (window.XLW_ENEMY.deck.length) {
        const drawnCard = window.XLW_ENEMY.deck.pop();
        const drawnName = (drawnCard && drawnCard.name) ? drawnCard.name : "未知卡牌";
        if (hasAngryPrajna) {
          exileCard(drawnCard, "enemy");
          logBattle(`憤怒的般若 效果：使對手強行棄置抽到的卡片 ${drawnName}！`);
        } else {
          window.XLW_ENEMY.hand.push(drawnCard);
          drawn++;
          if (hasSmartPrajna) {
            logBattle(`智慧的般若 效果：展示對手抽到的卡片：【${drawnName}】！`);
          }
        }
      }
    }""",
        """    // 2. 對手抽 2 張 (AI 抽牌階段)
    const enemyDrawn = [];
    for (let i = 0; i < 2; i++) {
      if (window.XLW_ENEMY.deck.length) {
        enemyDrawn.push(window.XLW_ENEMY.deck.pop());
      }
    }
    
    const hasSmartPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name.includes("智慧的般若"));
    const hasAngryPrajna = field["player_front"].concat(field["player_back"]).some(u => u && u.card && u.card.name.includes("憤怒的般若"));

    if (enemyDrawn.length > 0) {
      if (hasAngryPrajna) {
        // AI 選擇 1 張除外
        const exileIdx = Math.floor(Math.random() * enemyDrawn.length);
        const exiledCard = enemyDrawn[exileIdx];
        exileCard(exiledCard, "enemy");
        logBattle(`憤怒的般若 效果：對手選擇將抽出的卡片 ${exiledCard.name} 除外！`);
        
        enemyDrawn.forEach((c, idx) => {
          if (idx !== exileIdx) {
            window.XLW_ENEMY.hand.push(c);
          }
        });
      } else if (hasSmartPrajna) {
        // AI 選擇 1 張展示。AI 偏好選擇展示魔法卡以防我方進化
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
        
        // 展示給玩家看 (Popup)
        showRevealedCardModal(revealedCard, "對手");
        
        // 判斷是否為單位卡，若是則詢問玩家是否進化智慧的般若
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
              graveyard.push(unit.card);
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
              render();
            }
          }
        }
      } else {
        enemyDrawn.forEach(c => window.XLW_ENEMY.hand.push(c));
      }
    }"""
    ),
    # 3. Mulligan draw 1
    (
        """    if (isMyTurn) {
      turn = 1;
      phase = "召喚階段";
      draw(2);
      logBattle(`換牌完成（換了 ${replacedCards.length} 張），進入第 1 回合。已自動抽 2 張。`);""",
        """    if (isMyTurn) {
      turn = 1;
      phase = "召喚階段";
      await performPlayerTurnStartDraw();
      logBattle(`換牌完成（換了 ${replacedCards.length} 張），進入第 1 回合。已自動抽 2 張。`);"""
    ),
    # 4. Mulligan draw 2
    (
        """        isMyTurn = true;
        draw(2);
        phase = "召喚階段";
        setStatus("對手回合結束。目前為我方第 2 回合「召喚階段」，已自動抽 2 張。");""",
        """        isMyTurn = true;
        await performPlayerTurnStartDraw();
        phase = "召喚階段";
        setStatus("對手回合結束。目前為我方第 2 回合「召喚階段」，已自動抽 2 張。");"""
    ),
    # 5. Mulligan complete draw
    (
        """    draw(2);
    logBattle("雙方皆已完成起手換牌！第 1 回合對決正式開始。");
    
    const goFirst = (window.XLW_coinTossFirstGo !== undefined) ? window.XLW_coinTossFirstGo : (player_role === "player1");
    if (goFirst) {
      isMyTurn = true;
      setStatus("對決開始！第 1 回合為我方回合，召喚階段開始。");
    } else {
      isMyTurn = false;
      setStatus("對決開始！第 1 回合為對手回合，等待對手行動...");
    }""",
        """    logBattle("雙方皆已完成起手換牌！第 1 回合對決正式開始。");
    
    const goFirst = (window.XLW_coinTossFirstGo !== undefined) ? window.XLW_coinTossFirstGo : (player_role === "player1");
    if (goFirst) {
      isMyTurn = true;
      setStatus("對決開始！第 1 回合為我方回合，召喚階段開始。");
      await performPlayerTurnStartDraw();
    } else {
      isMyTurn = false;
      setStatus("對決開始！第 1 回合為對手回合，等待對手行動...");
      draw(2);
    }"""
    ),
    # 6. Turn start draw
    (
        """    // 回合開始自動抽 2 張
    draw(2);""",
        """    // 回合開始自動抽 2 張
    await performPlayerTurnStartDraw();"""
    ),
    # 7. WS end turn draw
    (
        """      // 動態更新對手的手牌與牌庫張數（對手回補抽了 2 張）
      if (window.XLW_ENEMY.hand) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.hand.push(null);
      }
      if (window.XLW_ENEMY.deck) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.deck.pop();
      }

      draw(2);
      if (window.XLW_DEFENSE_RULE.playerNeedsDefense && enemyHasAttackers) {""",
        """      // 動態更新對手的手牌與牌庫張數（對手回補抽了 2 張）
      if (window.XLW_ENEMY.hand) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.hand.push(null);
      }
      if (window.XLW_ENEMY.deck) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.deck.pop();
      }

      await performPlayerTurnStartDraw();
      if (window.XLW_DEFENSE_RULE.playerNeedsDefense && enemyHasAttackers) {"""
    ),
    # 8. WS extra summon resolved (Inserting WebSocket Handlers right before it)
    (
        """    } else if (data.action === "extra_summon_resolved") {""",
        """    } else if (data.action === "hannya_exile_drawn_card") {
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
              graveyard.push(unit.card);
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
      const oppZone = data.zone.replace("player_", "enemy_");
      const oppIdx = data.idx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        window.XLW_ENEMY.grave.push(oldUnit.card);
        enemyGraveyard = window.XLW_ENEMY.grave;
      }
      const extraIdx = enemyExtraDeck.findIndex(c => c && (c.id === "SR-VLG-0049" || c.name.includes("憤怒的般若")));
      if (extraIdx >= 0) {
        enemyExtraDeck.splice(extraIdx, 1);
      }
      field[oppZone][oppIdx] = {
        card: structuredClone(angryHannya),
        tapped: false,
        attacking: false,
        target: null,
        summonedTurn: turn,
        summonedZone: oppZone
      };
      logBattle(`✨ 額外進化：對手的【智慧的般若】已升級進化為【憤怒的般若】！`);
      playerBonusScore = Math.max(0, playerBonusScore - 1);
      render();
    } else if (data.action === "extra_summon_resolved") {"""
    )
]

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    print(f"\nProcessing {f_name}...")
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Run a dry-run check first
    all_ok = True
    content_lf = content.replace("\r\n", "\n")
    
    for idx, (target, replacement) in enumerate(replacements, 1):
        target_lf = target.replace("\r\n", "\n")
        cnt = content_lf.count(target_lf)
        if cnt != 1:
            print(f"  [ERROR] Pattern {idx} found {cnt} times instead of 1!")
            all_ok = False
            
    if not all_ok:
        print(f"  [ABORT] Aborting changes for {f_name} due to verification failure.")
        continue
        
    # Apply replacements
    new_content = content_lf
    for target, replacement in replacements:
        target_lf = target.replace("\r\n", "\n")
        replacement_lf = replacement.replace("\r\n", "\n")
        new_content = new_content.replace(target_lf, replacement_lf)
        
    # Write back
    with open(f_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"  [SUCCESS] All patterns replaced successfully in {f_name}.")
