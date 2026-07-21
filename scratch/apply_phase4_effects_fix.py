# -*- coding: utf-8 -*-
import sys

def main():
    filepath = "static/game_v8.js"
    try:
        code = open(filepath, encoding="utf-8").read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    def safe_replace(label, target, replacement):
        nonlocal code
        if target in code:
            code = code.replace(target, replacement)
            print(f"[{label}] Replaced successfully.")
        elif replacement in code:
            print(f"[{label}] Already replaced (skipped).")
        else:
            print(f"[{label}] Warning: target not found!")

    # 1. Sun Cake (太陽餅 R-FMS-0003) check in castSpell
    target_suncake_cast = """async function castSpell(handIndex) {
  try {
    xlwSanitizeGoatCardTypes();
    const card = hand[handIndex];"""

    replacement_suncake_cast = """async function castSpell(handIndex) {
  try {
    xlwSanitizeGoatCardTypes();
    const card = hand[handIndex];

    // R-FMS-0003 太陽餅 場地限制
    const isFieldSpell = card && (card.art_subtype === "場地" || card.magic_type === "場地" || card.name?.includes("場地") || card.name?.includes("世界") || card.name?.includes("電影院") || card.name?.includes("井") || card.name?.includes("鬼屋"));
    if (isFieldSpell) {
      let hasSunCake = false;
      for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
        field[z].forEach((u, i) => {
          if (u && u.card && (u.card.id === "R-FMS-0003" || u.card.name?.includes("太陽餅")) && !window.isUnitSilenced(u, z, i)) {
            hasSunCake = true;
          }
        });
      }
      if (hasSunCake) {
        setStatus("場上有太陽餅生效中，雙方不得使用場地魔法卡！");
        return;
      }
    }"""

    safe_replace("Sun Cake (太陽餅) check in castSpell", target_suncake_cast, replacement_suncake_cast)

    # 2. High Tower (高塔101號) Play Eligibility check in canSummonCard
    target_tower_play = """function canSummonCard(card, isPlayer) {
  if (card.id === "SSSR-NMS-0034" || card.name?.includes("火野貝")) {"""

    replacement_tower_play = """function canSummonCard(card, isPlayer) {
  // R-FMS-0030 / SSR-FMS-0030 高塔101號 限制
  if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
    const ok = window.xlwCheckMahjongCombo(isPlayer, "小四喜");
    if (!ok) {
      if (isPlayer) {
        setStatus("【召喚限制】高塔101號 需要我方場上備齊東、南、西、北！");
      }
      return false;
    }
  }

  if (card.id === "SSSR-NMS-0034" || card.name?.includes("火野貝")) {"""

    safe_replace("High Tower play eligibility check", target_tower_play, replacement_tower_play)

    # 3. AI unit play limits (Mahjong wildcard check for High Tower and Ma Zu)
    target_ai_unit_play = """      // 惡魔招財喵 (SR-CAT-0026) AI 手牌限制檢查
      let okToSummon = true;
      if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {"""

    replacement_ai_unit_play = """      // 惡魔招財喵 (SR-CAT-0026) AI 手牌限制檢查
      let okToSummon = true;
      if (card.id === "SR-CAT-0026" || card.name?.includes("惡魔招財喵")) {
        const oppGrave = window.XLW_ENEMY.grave || [];
        const catCount = oppGrave.filter(c => c && (c.deck === "喵喵賊" || c.faction === "喵喵賊" || c.id?.includes("CAT") || c.id?.includes("cat"))).length;
        if (catCount < 3) okToSummon = false;
      }
      
      // R-FMS-0030 / SSR-FMS-0030 高塔101號 AI 限制檢查
      if (card.id === "R-FMS-0030" || card.id === "SSR-FMS-0030" || card.name?.includes("高塔101號")) {
        const ok = window.xlwCheckMahjongCombo(false, "小四喜");
        if (!ok) okToSummon = false;
      }
      
      // SR-FMS-0036 麻祖 AI 限制檢查
      if (card.id === "SR-FMS-0036" || card.name?.includes("麻祖")) {
        const oppExile = enemyExileZone || [];
        const hasHu = oppExile.some(c => c && (c.id === "SR-FMS-0016" || c.id === "R-FMS-0017" || c.name?.includes("大三元") || c.name?.includes("小四喜")));
        if (!hasHu) okToSummon = false;
      }"""

    # We do a replacement of the whole block including the check logic
    safe_replace("AI unit play limits", target_ai_unit_play, replacement_ai_unit_play)

    # 4. Restore Mahjong unit names after turn end in xlwResolveEndPhaseEffects
    target_turn_end_restore = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {"""

    replacement_turn_end_restore = """window.xlwResolveEndPhaseEffects = async function(isPlayerSide) {
  // Restore Mahjong original names
  for (const z of ["player_front", "player_back", "enemy_front", "enemy_back"]) {
    field[z].forEach(u => {
      if (u && u.originalName) {
        u.card.name = u.originalName;
        u.originalName = null;
      }
    });
  }"""

    safe_replace("Restore Mahjong unit names after turn end", target_turn_end_restore, replacement_turn_end_restore)

    # Save the modified code back to static/game_v8.js
    open(filepath, "w", encoding="utf-8").write(code)
    print("All Happy Island changes written successfully.")

if __name__ == '__main__':
    main()
