import os

base_dir = "c:/Users/a2132/Documents/星靈王/XingLingWang_v7_fixed"

replacements = [
    # 1. AI auto-evolution in runEnemyTurn
    (
        """        if (hannyaSlot) {
          const { zone, idx } = hannyaSlot;
          const oldUnit = field[zone][idx];
          window.XLW_ENEMY.grave.push(oldUnit.card);
          enemyGraveyard = window.XLW_ENEMY.grave;
          logBattle(`[對手 額外召喚] 對手將場上的【般若】送入墓地作為素材。`);""",
        """        if (hannyaSlot) {
          const { zone, idx } = hannyaSlot;
          const oldUnit = field[zone][idx];
          exileCard(oldUnit.card, "enemy");
          logBattle(`[對手 額外召喚] 對手將場上的【般若】作為素材除外。`);"""
    ),
    # 2. Player manual evolution from extra deck modal (block 1)
    (
        """          const targetZone = selectedHannya.zone;
          const targetIdx = selectedHannya.idx;
          const oldHannya = selectedHannya.unit;
          
          graveyard.push(oldHannya.card);
          logBattle(`[額外召喚] 將場上的【般若】送入墓地作為素材。`);""",
        """          const targetZone = selectedHannya.zone;
          const targetIdx = selectedHannya.idx;
          const oldHannya = selectedHannya.unit;
          
          exileCard(oldHannya.card, "player");
          logBattle(`[額外召喚] 將場上的【般若】作為素材除外。`);"""
    ),
    # 3. Player manual evolution from extra deck modal (block 2)
    (
        """        const targetZone = selectedHannya.zone;
        const targetIdx = selectedHannya.idx;
        const oldHannya = selectedHannya.unit;
        
        graveyard.push(oldHannya.card);
        logBattle(`[額外召喚] 將場上的【般若】送入墓地作為素材。`);""",
        """        const targetZone = selectedHannya.zone;
        const targetIdx = selectedHannya.idx;
        const oldHannya = selectedHannya.unit;
        
        exileCard(oldHannya.card, "player");
        logBattle(`[額外召喚] 將場上的【般若】作為素材除外。`);"""
    ),
    # 4. AI evolution in performPlayerTurnStartDraw
    (
        """        if (hannyaSlots.length > 0 && angryCard) {
          const { zone, idx, unit } = hannyaSlots[0];
          window.XLW_ENEMY.grave.push(unit.card);
          enemyGraveyard = window.XLW_ENEMY.grave;
          enemyExtraDeck.splice(enemyExtraDeck.indexOf(angryCard), 1);""",
        """        if (hannyaSlots.length > 0 && angryCard) {
          const { zone, idx, unit } = hannyaSlots[0];
          exileCard(unit.card, "enemy");
          enemyExtraDeck.splice(enemyExtraDeck.indexOf(angryCard), 1);"""
    ),
    # 5. AI evolution in runEnemyTurn (under our new ai_draw_block) & WS hannya_reveal_drawn_card
    (
        """              const { zone, idx, unit } = selected;
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
        """              const { zone, idx, unit } = selected;
              exileCard(unit.card, "player");
              playerExtraDeck.splice(playerExtraDeck.indexOf(angryCard), 1);
              field[zone][idx] = {
                card: structuredClone(angryCard),
                tapped: false,
                attacking: false,
                target: null,
                summonedTurn: turn,
                summonedZone: zone
              };
              logBattle(`✨ 額外進化：【智慧的般若】成功升級為【憤怒的般若】！`);"""
    ),
    # 6. WS hannya_evolve_sync
    (
        """      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        window.XLW_ENEMY.grave.push(oldUnit.card);
        enemyGraveyard = window.XLW_ENEMY.grave;
      }""",
        """      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        exileCard(oldUnit.card, "enemy");
      }"""
    ),
    # 7. WS extra_summon_resolved
    (
        """    } else if (data.action === "extra_summon_resolved") {
      const oppZone = data.fromZone;
      const oppIdx = data.fromIdx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        window.XLW_ENEMY.grave.push(oldUnit.card);
        enemyGraveyard = window.XLW_ENEMY.grave;
        logBattle(`[額外召喚] 對手將場上的【般若】送入墓地作為素材。`);
      }""",
        """    } else if (data.action === "extra_summon_resolved") {
      const oppZone = data.fromZone;
      const oppIdx = data.fromIdx;
      const angryHannya = data.angryHannya;
      const oldUnit = field[oppZone][oppIdx];
      if (oldUnit) {
        exileCard(oldUnit.card, "enemy");
        logBattle(`[額外召喚] 對手將場上的【般若】作為素材除外。`);
      }"""
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
        
        # Pattern 5 matches exactly 2 times (reactive evolution in two different places)
        expected_cnt = 2 if idx == 5 else 1
        
        if cnt != expected_cnt:
            print(f"  [ERROR] Pattern {idx} found {cnt} times instead of {expected_cnt}!")
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
