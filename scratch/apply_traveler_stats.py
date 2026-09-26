import codecs

def inject_stats():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    atk_injection = '''
  // 特殊旅人預組 - SPT-0001 金白蘭旅人 / SPT-0016 派對旅人 攻擊力加成
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
    if (zone && lane !== undefined && field[zone]) {
      // SPT-0001 同排 +1
      for (let i = 0; i < 5; i++) {
        const u = field[zone][i];
        if (u && u.card && (u.card.id === "SPT-0001" || u.card.name?.includes("金白蘭旅人")) && !window.isUnitSilenced(u, zone, i) && i !== lane) {
          baseAtk += 1;
        }
      }
      // SPT-0016 左右 +1
      const adjSpaces = [lane - 1, lane + 1];
      for (const idx of adjSpaces) {
        if (idx >= 0 && idx < 5) {
          const adj = field[zone][idx];
          if (adj && adj.card && (adj.card.id === "SPT-0016" || adj.card.name?.includes("派對旅人")) && !window.isUnitSilenced(adj, zone, idx)) {
            baseAtk += 1;
          }
        }
      }
    }
  }
  return baseAtk + rainbowBonus;'''

    if 'SPT-0001' not in content[content.find('function getUnitAtk'):content.find('function getUnitAtk')+8000]:
        content = content.replace('return baseAtk + rainbowBonus;', atk_injection, 1)

    stars_injection = '''
  // 特殊旅人預組 - SPT-0001 金白蘭旅人 / SPT-0016 派對旅人 星數加成
  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {
    if (zone && lane !== undefined && field[zone]) {
      // SPT-0001 同排 +1
      for (let i = 0; i < 5; i++) {
        const u = field[zone][i];
        if (u && u.card && (u.card.id === "SPT-0001" || u.card.name?.includes("金白蘭旅人")) && !window.isUnitSilenced(u, zone, i) && i !== lane) {
          baseStars += 1;
        }
      }
      // SPT-0016 左右 +1
      const adjSpaces = [lane - 1, lane + 1];
      for (const idx of adjSpaces) {
        if (idx >= 0 && idx < 5) {
          const adj = field[zone][idx];
          if (adj && adj.card && (adj.card.id === "SPT-0016" || adj.card.name?.includes("派對旅人")) && !window.isUnitSilenced(adj, zone, idx)) {
            baseStars += 1;
          }
        }
      }
    }
  }
  return baseStars;'''

    if 'SPT-0001' not in content[content.find('function getUnitStars'):content.find('function getUnitStars')+8000]:
        content = content.replace('return baseStars;', stars_injection, 1)

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Injected stats successfully.")

inject_stats()
