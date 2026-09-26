import codecs
import re

def reinject_failed():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize to \n for internal search/replace
    content = content.replace('\\r\\n', '\\n')

    # 1. SPT-0001
    spt_0001_anchor = 'baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;\\n}'
    spt_0001_code = '''baseAtk = Number.isFinite(baseAtk) ? baseAtk : 0;
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

    if 'SPT-0001' not in content:
        if spt_0001_anchor in content:
            content = content.replace(spt_0001_anchor, spt_0001_code)
            print("[OK] SPT-0001 injected.")
        else:
            print("[FAILED] SPT-0001 anchor not found.")
    else:
        print("[ALREADY EXISTS] SPT-0001")


    # 2. SPT-0016
    spt_0016_anchor = 'let baseStars = Number(c.score ?? c.stars ?? 0) + Number(unit.bonusScore ?? 0);'
    spt_0016_code = '''let baseStars = Number(c.score ?? c.stars ?? 0) + Number(unit.bonusScore ?? 0);

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
}'''

    if 'SPT-0016' not in content:
        if spt_0016_anchor in content:
            content = content.replace(spt_0016_anchor, spt_0016_code)
            print("[OK] SPT-0016 injected.")
        else:
            print("[FAILED] SPT-0016 anchor not found.")
    else:
        print("[ALREADY EXISTS] SPT-0016")

    # 3. R-SPT-0014
    r_spt_0014_anchor = 'function isUnitMagicImmune(unit, zone, idx) {\\nif (!unit || !unit.card) return false;'
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

    if 'R-SPT-0014' not in content:
        # try regex for flexibility
        match = re.search(r'function isUnitMagicImmune\(unit, zone, idx\) \{\nif \(\!unit \|\| \!unit\.card\) return false;', content)
        if match:
            content = content.replace(match.group(0), r_spt_0014_code)
            print("[OK] R-SPT-0014 injected.")
        else:
            print("[FAILED] R-SPT-0014 anchor not found.")
    else:
        print("[ALREADY EXISTS] R-SPT-0014")

    # Save
    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)

reinject_failed()
