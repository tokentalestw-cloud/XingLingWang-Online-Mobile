import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

patterns = {
    "helper_insert": """function draw(n) {
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
    "ai_draw_block": """    // 2. 對手抽 2 張
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
    "mulligan_draw_1": """    if (isMyTurn) {
      turn = 1;
      phase = "召喚階段";
      draw(2);
      logBattle(`換牌完成（換了 ${replacedCards.length} 張），進入第 1 回合。已自動抽 2 張。`);""",
    "mulligan_draw_2": """        isMyTurn = true;
        draw(2);
        phase = "召喚階段";
        setStatus("對手回合結束。目前為我方第 2 回合「召喚階段」，已自動抽 2 張。");""",
    "mulligan_complete_draw": """    draw(2);
    logBattle("雙方皆已完成起手換牌！第 1 回合對決正式開始。");
    
    const goFirst = (window.XLW_coinTossFirstGo !== undefined) ? window.XLW_coinTossFirstGo : (player_role === "player1");
    if (goFirst) {
      isMyTurn = true;
      setStatus("對決開始！第 1 回合為我方回合，召喚階段開始。");
    } else {
      isMyTurn = false;
      setStatus("對決開始！第 1 回合為對手回合，等待對手行動...");
    }""",
    "turn_start_draw": """    // 回合開始自動抽 2 張
    draw(2);""",
    "ws_end_turn_draw": """      // 動態更新對手的手牌與牌庫張數（對手回補抽了 2 張）
      if (window.XLW_ENEMY.hand) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.hand.push(null);
      }
      if (window.XLW_ENEMY.deck) {
        for (let i = 0; i < 2; i++) window.XLW_ENEMY.deck.pop();
      }

      draw(2);
      if (window.XLW_DEFENSE_RULE.playerNeedsDefense && enemyHasAttackers) {""",
    "ws_extra_summon_resolved": """    } else if (data.action === "extra_summon_resolved") {"""
}

for f_name in ["static/game.js", "static/game_v8.js"]:
    f_path = os.path.join(base_dir, f_name)
    print(f"\nChecking patterns in {f_name}...")
    with open(f_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for p_name, p_val in patterns.items():
        p_val_lf = p_val.replace("\r\n", "\n")
        content_lf = content.replace("\r\n", "\n")
        count = content_lf.count(p_val_lf)
        print(f"  {p_name}: {count} occurrences")
