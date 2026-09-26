import codecs

def reinject_failed():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize newlines
    content = content.replace('\\r\\n', '\\n')

    replacements = []

    # 1. promptAndSummonTraveler
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
        "  let baseAtkNum = parseInt(baseAtk, 10);\\n  if (isNaN(baseAtkNum)) baseAtkNum = 0;",
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
        "function getUnitStars(unit, zone, idx) {\\n  if (!unit || !unit.card) return 0;\\n  const c = unit.card;\\n  let s = parseInt(c.score, 10) || 0;",
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
        'window.xlwResolveTurnStartEffects = async function(isPlayerSide) {\\nconst prefix = isPlayerSide ? "player_" : "enemy_";',
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
        "function isUnitMagicImmune(unit, zone, idx) {\\n  if (!unit || !unit.card) return false;\\n  const c = unit.card;",
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
    # We will search for '不可獻祭判定' with regex because encoding for chinese chars can be tricky.
    
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
            
    # Manually fix SPT-0013
    import re
    if 'SPT-0013' not in content:
        match = re.search(r'//\\s*不可獻祭判定\\n\\s*const c = unit\\.card \\|\\| unit;', content)
        if match:
            content = content.replace(match.group(0), spt_0013_code)
            print("[OK] SPT-0013 (toggleTributeSelection) injected.")
            success += 1
        else:
            print("[FAILED] SPT-0013 (toggleTributeSelection) - Anchor not found!")
    else:
        print("[ALREADY EXISTS] SPT-0013 (toggleTributeSelection)")
        success += 1

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Total injections: {success}/6")

reinject_failed()
