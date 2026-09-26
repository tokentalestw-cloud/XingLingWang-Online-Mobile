import codecs

with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;' in line:
        if 'SPT-0001' not in ''.join(lines[i:i+20]):
            print('Replacing SPT-0001...')
            new_lines = lines[:i+1] + [
                '  }\\r\\n',
                '\\r\\n',
                '  // 特殊旅人預組 - SPT-0001 金白蘭旅人 (每有1個其他旅人，攻擊力+1)\\r\\n',
                '  if (c.id === "SPT-0001" || c.name?.includes("金白蘭旅人")) {\\r\\n',
                '      let travelerCount = 0;\\r\\n',
                '      const isPlayer = zone && zone.startsWith("player_");\\r\\n',
                '      const sidePrefix = isPlayer ? "player_" : "enemy_";\\r\\n',
                '      for (const z of [sidePrefix + "front", sidePrefix + "back"]) {\\r\\n',
                '          field[z].forEach((u, i) => {\\r\\n',
                '              if (u && (z !== zone || i !== lane) && (u.card.id === "TOKEN_TRAVELER" || u.card.name?.includes("旅人") || u.card.name?.includes("小旅人"))) {\\r\\n',
                '                  travelerCount++;\\r\\n',
                '              }\\r\\n',
                '          });\\r\\n',
                '      }\\r\\n',
                '      baseAtk += travelerCount;\\r\\n',
                '  }\\r\\n'
            ] + lines[i+2:]
            lines = new_lines
        break

for i, line in enumerate(lines):
    if 'function isUnitMagicImmune(unit, zone, idx) {' in line:
        if 'R-SPT-0014' not in ''.join(lines[i:i+20]):
            print('Replacing R-SPT-0014...')
            new_lines = lines[:i+2] + [
                '  const c = unit.card;\\r\\n',
                '  // 特殊旅人預組 - R-SPT-0014 魔法旅人 (小旅人獲得魔法抗性)\\r\\n',
                '  if (c.id === "TOKEN_TRAVELER" || c.name?.includes("小旅人")) {\\r\\n',
                '      const side = (zone && zone.startsWith("player_")) ? "player_" : "enemy_";\\r\\n',
                '      const hasMagicTraveler = field[side + "front"].concat(field[side + "back"]).some((u, i) => {\\r\\n',
                '          let actualZone = i < 5 ? side + "front" : side + "back";\\r\\n',
                '          let actualIdx = i % 5;\\r\\n',
                '          return u && u.card && (u.card.id === "R-SPT-0014" || u.card.name?.includes("魔法旅人")) && !window.isUnitSilenced(u, actualZone, actualIdx);\\r\\n',
                '      });\\r\\n',
                '      if (hasMagicTraveler) return true;\\r\\n',
                '  }\\r\\n'
            ] + lines[i+2:]
            lines = new_lines
        break

with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
    f.writelines(lines)
