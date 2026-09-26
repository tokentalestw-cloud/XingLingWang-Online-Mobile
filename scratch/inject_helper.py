import codecs
import re

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    content = f.read()

helper_code = '''
// ===== 小旅人通用召喚函式 (供多種旅人卡牌使用) =====
async function promptAndSummonTraveler(side, count, sourceEffectName) {
  for (let i = 0; i < count; i++) {
    const zones = side === "player" ? ["player_front", "player_back"] : ["enemy_front", "enemy_back"];
    let hasEmptySlot = false;
    for (const z of zones) {
      if (field[z].some(x => !x)) { hasEmptySlot = true; break; }
    }
    if (!hasEmptySlot) {
      logBattle(`${sourceEffectName}：${side === "player" ? "我方" : "對手"}場上已滿，無法召喚小旅人。`);
      break;
    }
    
    const travelerCard = allCards.find(c => c && (c.id === "TOKEN_TRAVELER" || c.name.includes("小旅人"))) || { id: "TOKEN_TRAVELER", name: "小旅人", type: "unit", tribute: 0, attack: "1", score: 1 };
    
    if (side === "player") {
      window.XLW_receptionistPlacementActive = true;
      setStatus(`【${sourceEffectName}】請選擇我方一個空格特殊召喚小旅人！(${i+1}/${count})`);
      render();
      const placement = await new Promise(r => { window.XLW_receptionistResolve = r; });
      window.XLW_receptionistPlacementActive = false;
      if (placement) {
        field[placement.zone][placement.idx] = {
          card: structuredClone(travelerCard),
          tapped: false, attacking: false, target: null,
          summonedTurn: turn, summonedZone: placement.zone,
          equipments: []
        };
        logBattle(`✨ 【${sourceEffectName}】效果：在我方 ${placement.zone.includes("front") ? "前排" : "後排"}${placement.idx + 1} 特殊召喚一個小旅人！`);
        if (typeof animateCardDrop === 'function') animateCardDrop(placement.zone, placement.idx);
        
        // SR-SPT-0029 樹葉旅人觸發
        const leafTraveler = [...field.player_front, ...field.player_back].find(u => u && u.card && (u.card.id === "SR-SPT-0029" || u.card.name.includes("樹葉旅人")) && u.leafEffectUsedTurn !== turn);
        if (leafTraveler) {
            leafTraveler.leafEffectUsedTurn = turn;
            logBattle(`✨ 樹葉旅人 效果觸發：每回合限一次，召喚小旅人時追加召喚 1 個小旅人！`);
            await promptAndSummonTraveler("player", 1, "樹葉旅人");
        }
      }
    } else {
      let selectedSlot = null;
      for (const z of ["enemy_front", "enemy_back"]) {
        const emptyIndices = [];
        field[z].forEach((u, idx) => { if (!u) emptyIndices.push(idx); });
        if (emptyIndices.length > 0) {
          selectedSlot = { zone: z, idx: emptyIndices[0] };
          break;
        }
      }
      if (selectedSlot) {
        field[selectedSlot.zone][selectedSlot.idx] = {
          card: structuredClone(travelerCard),
          tapped: false, attacking: false, target: null,
          summonedTurn: turn, summonedZone: selectedSlot.zone,
          equipments: []
        };
        logBattle(`✨ 對手的【${sourceEffectName}】效果：在 ${selectedSlot.zone.includes("front") ? "前排" : "後排"}${selectedSlot.idx + 1} 特殊召喚一個小旅人！`);
        if (typeof animateCardDrop === 'function') animateCardDrop(selectedSlot.zone, selectedSlot.idx);
        
        const leafTraveler = [...field.enemy_front, ...field.enemy_back].find(u => u && u.card && (u.card.id === "SR-SPT-0029" || u.card.name.includes("樹葉旅人")) && u.leafEffectUsedTurn !== turn);
        if (leafTraveler) {
            leafTraveler.leafEffectUsedTurn = turn;
            logBattle(`✨ 對手 樹葉旅人 效果觸發：每回合限一次，召喚小旅人時追加召喚 1 個小旅人！`);
            await promptAndSummonTraveler("enemy", 1, "樹葉旅人");
        }
      }
    }
  }
  render();
}

window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
'''

if 'async function promptAndSummonTraveler' not in content:
    content = content.replace('window.xlwResolveTurnStartEffects = async function(isPlayerSide) {', helper_code)
    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected promptAndSummonTraveler successfully.")
else:
    print("promptAndSummonTraveler already injected.")
