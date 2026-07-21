# -*- coding: utf-8 -*-
import sys, re

def fix_ai_traveler_fallback():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Define helper logic for AI fallback unit search
    # Replace LITTLE_TRAVELER fallback in runEnemyTurn
    old_fallback_1 = """field[destZone][destIdx] = {
          card: structuredClone(LITTLE_TRAVELER),
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: destZone
        };
        field[destZone][destIdx].card.creator = "enemy";
        window.XLW_enemySummonCountThisTurn = (window.XLW_enemySummonCountThisTurn || 0) + 1;
        logBattle(`🤖【對手 AI 召喚】手牌無免祭品單位，自動戰術特召【小旅人】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}！`);
        try { playTravelerSummonAnimation("#enemyForest", destZone, destIdx); } catch (e) {}"""

    new_fallback_1 = """const aiDeckUnit = (window.XLW_ENEMY.deck || []).find(c => c && c.type === "unit" && getCardTributeCost(c) === 0) ||
                           allCards.find(c => c && c.type === "unit" && getCardTributeCost(c) === 0 && (c.deck === (window.XLW_ENEMY.deckName || "妖怪村莊") || c.faction === (window.XLW_ENEMY.deckName || "妖怪村莊"))) ||
                           { id: "C-VLG-0001", name: "小妖怪", type: "unit", tribute: 0, attack: 2, score: 1, image: "/static/card_images/c_vlg_0001.jpeg" };
        const fallbackCard = structuredClone(aiDeckUnit);
        field[destZone][destIdx] = {
          card: fallbackCard,
          tapped: false,
          attacking: false,
          target: null,
          summonedTurn: turn,
          summonedZone: destZone
        };
        field[destZone][destIdx].card.creator = "enemy";
        window.XLW_enemySummonCountThisTurn = (window.XLW_enemySummonCountThisTurn || 0) + 1;
        logBattle(`🤖【對手 AI 召喚】打出單位【${fallbackCard.name}】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}！`);"""

    old_fallback_2 = """field[destZone][destIdx] = {
              card: structuredClone(LITTLE_TRAVELER),
              tapped: false,
              attacking: false,
              target: null,
              summonedTurn: turn,
              summonedZone: destZone
            };
            logBattle(`🤖【對手 AI 戰術佈陣】無常規單位可召喚，強制特召【小旅人】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);
            try {
              playTravelerSummonAnimation("#enemyForest", destZone, destIdx);
            } catch (e) {}"""

    new_fallback_2 = """const aiDeckUnit = (window.XLW_ENEMY.deck || []).find(c => c && c.type === "unit" && getCardTributeCost(c) === 0) ||
                               allCards.find(c => c && c.type === "unit" && getCardTributeCost(c) === 0 && (c.deck === (window.XLW_ENEMY.deckName || "妖怪村莊") || c.faction === (window.XLW_ENEMY.deckName || "妖怪村莊"))) ||
                               { id: "C-VLG-0001", name: "小妖怪", type: "unit", tribute: 0, attack: 2, score: 1, image: "/static/card_images/c_vlg_0001.jpeg" };
            const fallbackCard = structuredClone(aiDeckUnit);
            field[destZone][destIdx] = {
              card: fallbackCard,
              tapped: false,
              attacking: false,
              target: null,
              summonedTurn: turn,
              summonedZone: destZone
            };
            logBattle(`🤖【對手 AI 戰術佈陣】打出單位【${fallbackCard.name}】到對手${destZone === "enemy_front" ? "前排" : "後排"}${destIdx + 1}`);"""

    if old_fallback_1 in js_content:
        js_content = js_content.replace(old_fallback_1, new_fallback_1)
        print("Replaced fallback 1 successfully!")

    if old_fallback_2 in js_content:
        js_content = js_content.replace(old_fallback_2, new_fallback_2)
        print("Replaced fallback 2 successfully!")

    # Also clean up any lingering LITTLE_TRAVELER prompt text in showXLWConfirm calls
    js_content = js_content.replace("對手召喚了【小旅人】", "對手召喚了單位")

    open(js_path, 'w', encoding='utf-8').write(js_content)

    # Update cache-buster in index.html to v=9.50-ai-traveler-fallback-removed
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.50-ai-traveler-fallback-removed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.50-ai-traveler-fallback-removed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_ai_traveler_fallback()
