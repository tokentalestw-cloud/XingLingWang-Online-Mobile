# -*- coding: utf-8 -*-
import sys, re

def apply_ultra_3d():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update renderEnemyPanel in static/game_v8.js for 3D stat pills
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_enemy_panel_func = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  const deckName = window.XLW_ENEMY.deckName || "\\u5996\\u602a\\u6751\\u83aa";
  panel.innerHTML = `
    <div class="enemy-info-title">\\u5c0d\\u624b\\u72c0\\u614b\\uff1a${deckName}</div>
    <div>\\u5c0d\\u624b\\u724c\\u5eab\\uff1a<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span></div>
    <div>\\u5c0d\\u624b\\u624b\\u724c\\uff1a<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span></div>
  `;
}"""

    new_enemy_panel_func = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  const deckName = window.XLW_ENEMY.deckName || "妖怪村莊";
  panel.innerHTML = `
    <div class="enemy-info-title">👾 對手狀態：<span class="enemy-deck-tag">${deckName}</span></div>
    <div class="enemy-stats-row" style="display: flex; gap: 8px; margin-top: 6px;">
      <div class="enemy-stat-badge">🎴 牌庫：<span id="enemyDeckCountInfo">${window.XLW_ENEMY.deck.length}</span> 張</div>
      <div class="enemy-stat-badge">🃏 手牌：<span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;
}"""

    if "function renderEnemyPanel()" in js_content:
        # Regex replacement for renderEnemyPanel
        js_content = re.sub(r'function renderEnemyPanel\(\) \{.*?\n\}', new_enemy_panel_func, js_content, flags=re.DOTALL)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("1. Updated renderEnemyPanel in static/game_v8.js with 3D badges successfully!")

    # 2. Append ultra 3D CSS rules to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    ultra_3d_css = """

/* ==========================================================================
   ULTRA-LEVELED 3D SCORE BOXES & OPPONENT STATUS PANEL
   (對手狀態欄與雙方總分深度 3D 浮雕、立體徽章與金色光暈重構)
   ========================================================================== */

/* 1. 對手狀態欄位 (#xlwEnemyInfoPanel) 立體與戰術徽章 */
#xlwEnemyInfoPanel, .xlw-enemy-info-panel {
  background: radial-gradient(circle at 50% 20%, rgba(255, 77, 79, 0.22) 0%, transparent 75%), linear-gradient(180deg, rgba(48, 20, 32, 0.98) 0%, rgba(20, 8, 16, 0.99) 100%) !important;
  border: 2px solid #ff7875 !important;
  border-bottom: 5px solid #870003 !important;
  border-radius: 18px !important;
  color: #fff0f2 !important;
  padding: 14px 18px !important;
  font-weight: 900 !important;
  box-shadow: inset 0 2px 4px rgba(255, 255, 255, 0.45), inset 0 -4px 8px rgba(0, 0, 0, 0.6), 0 12px 35px rgba(0, 0, 0, 0.95), 0 0 25px rgba(255, 77, 79, 0.45) !important;
  backdrop-filter: blur(14px) !important;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease !important;
}

#xlwEnemyInfoPanel:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: inset 0 2.5px 5px rgba(255, 255, 255, 0.75), inset 0 -4px 8px rgba(0, 0, 0, 0.6), 0 16px 40px rgba(0, 0, 0, 0.98), 0 0 32px rgba(255, 77, 79, 0.65) !important;
}

#xlwEnemyInfoPanel .enemy-info-title {
  color: #ff9c9e !important;
  font-size: 16px !important;
  font-weight: 900 !important;
  text-shadow: 0 0 12px rgba(255, 77, 79, 0.8), 2px 2px 0 #000 !important;
  letter-spacing: 0.6px !important;
}

#xlwEnemyInfoPanel .enemy-deck-tag {
  color: #ffe600 !important;
  background: rgba(0, 0, 0, 0.5) !important;
  border: 1px solid #ffe600 !important;
  border-radius: 6px !important;
  padding: 2px 8px !important;
  font-size: 13px !important;
  text-shadow: 1px 1px 0 #000 !important;
  box-shadow: inset 0 1px 2px rgba(255,255,255,0.4), 0 2px 6px rgba(0,0,0,0.5) !important;
}

.enemy-stat-badge {
  background: linear-gradient(180deg, rgba(255,255,255,0.2) 0%, rgba(0,0,0,0.55) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.75) !important;
  border-bottom: 3.5px solid #735900 !important;
  border-radius: 10px !important;
  padding: 5px 12px !important;
  font-size: 13px !important;
  font-weight: 900 !important;
  color: #ffffff !important;
  box-shadow: inset 0 1.5px 0 rgba(255, 255, 255, 0.5), 0 4px 10px rgba(0, 0, 0, 0.6) !important;
}

.enemy-stat-badge span {
  color: #ffe600 !important;
  font-size: 15px !important;
  font-weight: 900 !important;
  text-shadow: 0 0 8px rgba(255, 230, 0, 0.8), 1px 1px 0 #000 !important;
}

/* 2. 雙方總分對戰面板與歷史對話框 (.score-box & .score-row) */
.score-box {
  background: radial-gradient(circle at 50% 20%, rgba(255, 215, 0, 0.18) 0%, transparent 75%), linear-gradient(180deg, rgba(38, 28, 54, 0.98) 0%, rgba(16, 12, 24, 0.99) 100%) !important;
  border: 2.5px solid #ffe600 !important;
  border-bottom: 5.5px solid #8c6d00 !important;
  border-radius: 20px !important;
  color: #ffffff !important;
  box-shadow: inset 0 2.5px 5px rgba(255, 255, 255, 0.6), inset 0 -5px 10px rgba(0, 0, 0, 0.7), 0 16px 45px rgba(0, 0, 0, 0.95), 0 0 30px rgba(255, 230, 0, 0.45) !important;
  padding: 24px !important;
}

.score-row {
  background: linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(0,0,0,0.45) 100%) !important;
  border: 1.5px solid rgba(255, 230, 100, 0.6) !important;
  border-bottom: 3.5px solid #665000 !important;
  border-radius: 12px !important;
  padding: 10px 16px !important;
  margin: 10px 0 !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.4), 0 4px 12px rgba(0,0,0,0.6) !important;
  transition: transform 0.2s ease !important;
}

.score-row:hover {
  transform: translateY(-2px) scale(1.01) !important;
  border-color: #ffe600 !important;
  box-shadow: inset 0 2px 3px #ffffff, 0 6px 16px rgba(0,0,0,0.7), 0 0 16px rgba(255,230,0,0.4) !important;
}

.score-row b {
  font-size: 15px !important;
  font-weight: 900 !important;
  color: #ffffff !important;
  text-shadow: 1px 1px 2px #000 !important;
}

.score-row span {
  font-size: 18px !important;
  font-weight: 900 !important;
}

#xlwPlayerScore, #xlwEnemyScore, .score-val, #enemyScoreVal, #playerScoreVal {
  display: inline-block !important;
  background: linear-gradient(180deg, rgba(255,255,255,0.25) 0%, rgba(0,0,0,0.5) 100%) !important;
  border: 1.5px solid #ffe600 !important;
  border-bottom: 3px solid #8c6d00 !important;
  border-radius: 10px !important;
  padding: 3px 12px !important;
  color: #ffe600 !important;
  font-weight: 900 !important;
  text-shadow: 0 0 12px rgba(255, 230, 0, 0.9), 1.5px 1.5px 0 #000 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 3px 8px rgba(0,0,0,0.6), 0 0 12px rgba(255,230,0,0.5) !important;
}

#xlwEnemyScore {
  border-color: #ff4d4f !important;
  border-bottom-color: #870003 !important;
  color: #ff7875 !important;
  text-shadow: 0 0 12px rgba(255, 77, 79, 0.9), 1.5px 1.5px 0 #000 !important;
  box-shadow: inset 0 1.5px 0 #ffffff, 0 3px 8px rgba(0,0,0,0.6), 0 0 12px rgba(255,77,79,0.5) !important;
}

"""

    css_content += ultra_3d_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended ultra 3D score box & opponent status panel CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.40-ultra-3d-scores-enemy-panel
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.40-ultra-3d-scores-enemy-panel', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.40-ultra-3d-scores-enemy-panel', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_ultra_3d()
