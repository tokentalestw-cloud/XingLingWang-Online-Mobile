import codecs

def apply_fixes():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 1. xlwResolveTurnStartEffects (lines 27596-27597 -> index 27595:27597)
    r_spt_0008 = """window.xlwResolveTurnStartEffects = async function(isPlayerSide) {
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
  }\n"""
    if "window.xlwResolveTurnStartEffects" in lines[27595]:
        lines[27595:27597] = [r_spt_0008]
    else:
        print("ERROR: xlwResolveTurnStartEffects anchor mismatch at line 27596")
        return

    # 2. isUnitMagicImmune (lines 11871-11873 -> index 11870:11873)
    r_spt_0014 = """function isUnitMagicImmune(unit, zone, idx) {
  if (!unit || !unit.card) return false;
  
  const c = unit.card;
  // 特殊旅人預組 - R-SPT-0014 魔法旅人 (小旅人獲得魔法抗性)
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
    const side = (zone && zone.startsWith("player_")) ? "player_" : "enemy_";
    const hasMagicTraveler = field[side + "front"].concat(field[side + "back"]).some(u => u && u.card && (u.card.id === "R-SPT-0014" || u.card.name?.includes("魔法旅人")) && !window.isUnitSilenced(u, side, field[side+"front"].includes(u)?field[side+"front"].indexOf(u):field[side+"back"].indexOf(u)));
    if (hasMagicTraveler) return true;
  }

  let z = zone;\n"""
    if "function isUnitMagicImmune" in lines[11870]:
        lines[11870:11873] = [r_spt_0014]
    else:
        print("ERROR: isUnitMagicImmune anchor mismatch at line 11871")
        return

    # 3. getUnitStars (lines 2887-2888 -> index 2886:2888)
    spt_0016 = """  const c = unit.card || unit;
  let baseStars = Number(c.score ?? c.stars ?? 0) + Number(unit.bonusScore ?? 0);

  // 特殊旅人預組 - SPT-0016 派對旅人 (每有1個其他小旅人，星數+1)
  if (c.id === "SPT-0016" || c.name?.includes("派對旅人")) {
      let travelerCount = 0;
      const isPlayer = zone && zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      baseStars += travelerCount;
  }\n"""
    if "const c = unit.card || unit" in lines[2886]:
        lines[2886:2888] = [spt_0016]
    else:
        print("ERROR: getUnitStars anchor mismatch at line 2887")
        return

    # 4. getUnitAtk (lines 2516-2519 -> index 2515:2519)
    spt_0001 = """  if (!isShield) {
    baseAtk = Number(c.attack ?? c.atk ?? 0);
    baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;
  }

  // 特殊旅人預組 - SPT-0001 金白蘭旅人 (每有1個其他旅人，攻擊力+1)
  if (c.id === "SPT-0001" || c.name?.includes("金白蘭旅人")) {
      let travelerCount = 0;
      const isPlayer = zone && zone.startsWith("player_");
      const sidePrefix = isPlayer ? "player_" : "enemy_";
      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {
          field[z].forEach((u, i) => {
              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("旅人") || u.card.name?.includes("小旅人"))) {
                  travelerCount++;
              }
          });
      }
      baseAtk += travelerCount;
  }\n"""
    if "if (!isShield)" in lines[2515]:
        lines[2515:2519] = [spt_0001]
    else:
        print("ERROR: getUnitAtk anchor mismatch at line 2516")
        return

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print("All 4 missing travelers injected successfully!")

apply_fixes()
