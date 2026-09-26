import codecs
import re

def reinject_failed():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Helper Function
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

window.isCombineUnit = function(unit) {'''
    if 'promptAndSummonTraveler' not in content:
        match = re.search(r'window\.isCombineUnit = function\(unit\) \{', content)
        if match:
            content = content.replace(match.group(0), helper_code)
            print("[OK] Helper function injected.")
        else:
            print("[FAILED] Helper function anchor not found.")
    else:
        print("[ALREADY EXISTS] Helper function")

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
    if 'SPT-0001' not in content:
        match = re.search(r'let baseAtkNum = parseInt\(baseAtk, 10\);\r?\n\s*if \(isNaN\(baseAtkNum\)\) baseAtkNum = 0;', content)
        if match:
            content = content.replace(match.group(0), spt_0001_code)
            print("[OK] SPT-0001 injected.")
        else:
            print("[FAILED] SPT-0001 anchor not found.")
    else:
        print("[ALREADY EXISTS] SPT-0001")

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
    if 'SPT-0016' not in content:
        match = re.search(r'function getUnitStars\(unit, zone, idx\) \{\r?\n\s*if \(\!unit \|\| \!unit\.card\) return 0;\r?\n\s*const c = unit\.card;\r?\n\s*let s = parseInt\(c\.score, 10\) \|\| 0;', content)
        if match:
            content = content.replace(match.group(0), spt_0016_code)
            print("[OK] SPT-0016 injected.")
        else:
            print("[FAILED] SPT-0016 anchor not found.")
    else:
        print("[ALREADY EXISTS] SPT-0016")

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
    if 'R-SPT-0008' not in content:
        match = re.search(r'window\.xlwResolveTurnStartEffects = async function\(isPlayerSide\) \{\r?\n\s*const prefix = isPlayerSide \? "player_" : "enemy_";', content)
        if match:
            content = content.replace(match.group(0), r_spt_0008_code)
            print("[OK] R-SPT-0008 injected.")
        else:
            print("[FAILED] R-SPT-0008 anchor not found.")
    else:
        print("[ALREADY EXISTS] R-SPT-0008")

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
    if 'R-SPT-0014' not in content:
        match = re.search(r'function isUnitMagicImmune\(unit, zone, idx\) \{\r?\n\s*if \(\!unit \|\| \!unit\.card\) return false;\r?\n\s*const c = unit\.card;', content)
        if match:
            content = content.replace(match.group(0), r_spt_0014_code)
            print("[OK] R-SPT-0014 injected.")
        else:
            print("[FAILED] R-SPT-0014 anchor not found.")
    else:
        print("[ALREADY EXISTS] R-SPT-0014")

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)

reinject_failed()
