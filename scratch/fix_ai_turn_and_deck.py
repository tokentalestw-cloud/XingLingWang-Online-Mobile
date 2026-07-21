# -*- coding: utf-8 -*-
import sys

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')
    filepath = 'static/game_v8.js'
    content = open(filepath, encoding='utf-8').read()

    # 1. Update xlwInitEnemyDeck to accept deckName parameter
    old_init_enemy = """function xlwInitEnemyDeck() {
  const baseCards = strictSourceCards("妖怪村莊");
  window.XLW_ENEMY.deck = baseCards.map(c => structuredClone(c));
  shuffle(window.XLW_ENEMY.deck);
  window.XLW_ENEMY.hand = [];
  window.XLW_ENEMY.grave = [];
  enemyGraveyard = window.XLW_ENEMY.grave;
  enemyExtraDeck = xlwInitExtraDeck("妖怪村莊");"""

    new_init_enemy = """function xlwInitEnemyDeck(deckName = "妖怪村莊") {
  const selectedDeck = deckName || "妖怪村莊";
  const baseCards = strictSourceCards(selectedDeck);
  window.XLW_ENEMY.deck = baseCards.map(c => {
    const cloned = structuredClone(c);
    cloned.ownerSide = "enemy";
    return cloned;
  });
  shuffle(window.XLW_ENEMY.deck);
  window.XLW_ENEMY.hand = [];
  window.XLW_ENEMY.grave = [];
  window.XLW_ENEMY.deckName = selectedDeck;
  window.XLW_ENEMY.running = false;
  enemyGraveyard = window.XLW_ENEMY.grave;
  enemyExtraDeck = xlwInitExtraDeck(selectedDeck).map(c => {
    const cloned = structuredClone(c);
    cloned.ownerSide = "enemy";
    return cloned;
  });"""

    if old_init_enemy in content:
        content = content.replace(old_init_enemy, new_init_enemy)
        print("Updated xlwInitEnemyDeck function signature and deck creation")

    # 2. Update newGame() to read selected AI deck from dropdown
    old_new_game = """  // 妖怪村莊對手初始化
  xlwInitEnemyDeck();"""

    new_new_game = """  // 對手 AI 牌組選擇與初始化
  const aiDeckSelect = $("aiDeckSelect");
  let aiDeckChoice = aiDeckSelect ? aiDeckSelect.value : "隨機";
  if (aiDeckChoice === "隨機" || !aiDeckChoice) {
    const availableAIDecks = ["妖怪村莊", "發電獸", "碳碳族", "藝術品", "喵喵賊", "獸人", "虛擬世界", "勇者公會", "歡樂島"];
    aiDeckChoice = availableAIDecks[Math.floor(Math.random() * availableAIDecks.length)];
  }
  xlwInitEnemyDeck(aiDeckChoice);
  logBattle(`🎮 單人對決開始！我方使用【${deckName}】牌組，對手 AI 使用【${aiDeckChoice}】牌組！`);"""

    if old_new_game in content:
        content = content.replace(old_new_game, new_new_game)
        print("Updated newGame() to load selected AI deck")

    # 3. Ensure window.XLW_ENEMY.running is reset in runEnemyTurn
    old_running_check = """  if (window.XLW_ENEMY.running) return;
  window.XLW_ENEMY.running = true;"""

    new_running_check = """  if (window.XLW_ENEMY.running) {
    console.warn("AI runEnemyTurn was flagged running. Resetting flag and executing turn.");
  }
  window.XLW_ENEMY.running = true;"""

    if old_running_check in content:
        content = content.replace(old_running_check, new_running_check)
        print("Safeguarded window.XLW_ENEMY.running flag in runEnemyTurn")

    # 4. Enhance AI summon logic to support tribute summons for high-cost units
    old_summon_idx = """    const summonHandIdx = window.XLW_ENEMY.hand.findIndex(c =>
      c && (c.type === "unit" || c.type === "單位") && Number(c.tribute || 0) <= 0
    );"""

    new_summon_idx = """    let summonHandIdx = window.XLW_ENEMY.hand.findIndex(c =>
      c && (c.type === "unit" || c.type === "單位") && getCardTributeCost(c) <= 0
    );
    let tributeUnitsToSacrifice = [];

    if (summonHandIdx < 0) {
      const aiAvailableUnits = [];
      for (const z of ["enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u.card) aiAvailableUnits.push({ zone: z, idx: i, unit: u });
        });
      }
      aiAvailableUnits.sort((a, b) => getUnitAtk(a.unit, a.zone, a.idx) - getUnitAtk(b.unit, b.zone, b.idx));

      for (let i = 0; i < window.XLW_ENEMY.hand.length; i++) {
        const c = window.XLW_ENEMY.hand[i];
        if (c && (c.type === "unit" || c.type === "單位")) {
          const cost = getCardTributeCost(c);
          if (cost > 0 && aiAvailableUnits.length >= cost) {
            summonHandIdx = i;
            tributeUnitsToSacrifice = aiAvailableUnits.slice(0, cost);
            break;
          }
        }
      }
    }"""

    if old_summon_idx in content:
        content = content.replace(old_summon_idx, new_summon_idx)
        print("Enhanced AI summon index search with tribute summon support")

    # 5. Execute tribute sacrifice if required for AI summon
    old_ai_summon_exec = """    if (aiCanSummon) {
      window.XLW_ENEMY.hand.splice(summonHandIdx, 1);"""

    new_ai_summon_exec = """    if (aiCanSummon) {
      if (tributeUnitsToSacrifice.length > 0) {
        for (const sac of tributeUnitsToSacrifice) {
          await window.xlwEnemyTributeUnit(sac.unit, sac.zone, sac.idx);
          field[sac.zone][sac.idx] = null;
        }
        logBattle(`✨ 對手 AI 獻祭了 ${tributeUnitsToSacrifice.length} 個單位進行獻祭召喚！`);
        render();
      }
      window.XLW_ENEMY.hand.splice(summonHandIdx, 1);"""

    if old_ai_summon_exec in content:
        content = content.replace(old_ai_summon_exec, new_ai_summon_exec)
        print("Added tribute sacrifice execution before AI unit placement")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Saved all AI turn and AI deck choice fixes to static/game_v8.js")

if __name__ == '__main__':
    apply_fixes()
