import codecs

def inject_r_spt_0008():
    with codecs.open('static/game_v8.js', 'r', encoding='utf-8') as f:
        content = f.read()

    content = content.replace('\r\n', '\n')

    old = '''const prefix = isPlayerSide ? "player_" : "enemy_";

// 進化型態 / 特殊 布偶與特殊效果'''

    new_c = '''const prefix = isPlayerSide ? "player_" : "enemy_";

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

// 進化型態 / 特殊 布偶與特殊效果'''

    if old in content:
        content = content.replace(old, new_c)
        print("[OK] R-SPT-0008 injected.")
    elif new_c in content:
        print("[ALREADY EXISTS] R-SPT-0008")
    else:
        print("[FAILED] R-SPT-0008 - Anchor not found!")

    with codecs.open('static/game_v8.js', 'w', encoding='utf-8') as f:
        f.write(content)

inject_r_spt_0008()
