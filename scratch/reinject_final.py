import codecs

def reinject_last_two():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. R-SPT-0014
    r_spt_0014_anchor = 'function isUnitMagicImmune(unit, zone, idx) {\\r\\n  if (!unit || !unit.card) return false;'
    r_spt_0014_code = '''function isUnitMagicImmune(unit, zone, idx) {
  if (!unit || !unit.card) return false;
  const c = unit.card;
  // 特殊旅人預組 - R-SPT-0014 魔法旅人 (小旅人獲得魔法抗性)
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
      const side = (zone && zone.startsWith("player_")) ? "player_" : "enemy_";
      const hasMagicTraveler = field[side + "front"].concat(field[side + "back"]).some((u, i) => {
          let actualZone = i < 5 ? side + "front" : side + "back";
          let actualIdx = i % 5;
          return u && u.card && (u.card.id === "R-SPT-0014" || u.card.name?.includes("魔法旅人")) && !window.isUnitSilenced(u, actualZone, actualIdx);
      });
      if (hasMagicTraveler) return true;
  }'''
    r_spt_0014_code = r_spt_0014_code.replace('\\n', '\\r\\n')
    if 'R-SPT-0014' not in content:
        content = content.replace(r_spt_0014_anchor, r_spt_0014_code)
        print("[OK] R-SPT-0014 injected")
    else:
        print("[ALREADY EXISTS] R-SPT-0014")

    # 2. SPT-0001
    spt_0001_anchor = '    baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;\\r\\n  }'
    spt_0001_code = '''    baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;
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
  }'''
    spt_0001_code = spt_0001_code.replace('\\n', '\\r\\n')
    if 'SPT-0001' not in content:
        content = content.replace(spt_0001_anchor, spt_0001_code)
        print("[OK] SPT-0001 injected")
    else:
        print("[ALREADY EXISTS] SPT-0001")


    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)

reinject_last_two()
