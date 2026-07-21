import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

patterns = {
    # 1. AI auto-evolution in runEnemyTurn
    "ai_run_turn_evolve": """        if (hannyaSlot) {
          const { zone, idx } = hannyaSlot;
          const oldUnit = field[zone][idx];
          window.XLW_ENEMY.grave.push(oldUnit.card);
          enemyGraveyard = window.XLW_ENEMY.grave;
          logBattle(`[對手 額外召喚] 對手將場上的【般若】送入墓地作為素材。`);""",
          
    # 2. Player manual evolution from extra deck modal (block 1)
    "player_manual_evolve_1": """          const targetZone = selectedHannya.zone;
          const targetIdx = selectedHannya.idx;
          const oldHannya = selectedHannya.unit;
          
          graveyard.push(oldHannya.card);
          logBattle(`[額外召喚] 將場上的【般若】送入墓地作為素材。`);""",
          
    # 3. Player manual evolution from extra deck modal (block 2)
    "player_manual_evolve_2": """        const targetZone = selectedHannya.zone;
        const targetIdx = selectedHannya.idx;
        const oldHannya = selectedHannya.unit;
        
        graveyard.push(oldHannya.card);
        logBattle(`[額外召喚] 將場上的【般若】送入墓地作為素材。`);""",
        
    # 4. AI evolution in performPlayerTurnStartDraw
    "ai_perform_draw_evolve": """        if (hannyaSlots.length > 0 && angryCard) {
          const { zone, idx, unit } = hannyaSlots[0];
          window.XLW_ENEMY.grave.push(unit.card);
          enemyGraveyard = window.XLW_ENEMY.grave;
          enemyExtraDeck.splice(enemyExtraDeck.indexOf(angryCard), 1);""",
          
    # 5. AI evolution in runEnemyTurn (under our new ai_draw_block) & WS hannya_reveal_drawn_card
    "player_reactive_evolve_ai_turn": """              const { zone, idx, unit } = selected;
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
              logBattle(`✨ 額外進化：【智慧的般若】成功升級為【憤怒的般若】！`);""",
              
    # 6. WS hannya_evolve_sync
    "ws_hannya_evolve_sync": """      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        window.XLW_ENEMY.grave.push(oldUnit.card);
        enemyGraveyard = window.XLW_ENEMY.grave;
      }""",
    
    # 7. WS extra_summon_resolved
    "ws_extra_summon_resolved": """    } else if (data.action === "extra_summon_resolved") {
      const oppZone = data.fromZone;
      const oppIdx = data.fromIdx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        window.XLW_ENEMY.grave.push(oldUnit.card);
        enemyGraveyard = window.XLW_ENEMY.grave;
        logBattle(`[額外召喚] 對手將場上的【般若】送入墓地作為素材。`);
      }"""
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
