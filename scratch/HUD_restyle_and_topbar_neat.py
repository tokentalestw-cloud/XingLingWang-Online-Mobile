# -*- coding: utf-8 -*-
import sys, re

def hud_restyle_and_topbar_neat():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update renderEnemyPanel in static/game_v8.js
    js_content = open(js_path, encoding='utf-8').read()

    old_render_enemy = """function renderEnemyPanel() {
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

    new_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important;">👾 對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Simplified renderEnemyPanel in game_v8.js successfully!")

    # 2. Modify static/style_v8.css: Reposition panels and restyle topbar
    css_content = open(css_path, encoding='utf-8').read()

    # Update #xlwEnemyInfoPanel positioning in landscape query
    old_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 8px !important;
    top: 140px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 230px !important;
  }"""

    new_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 180px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Update #phaseDisplayPanelHard positioning in landscape query
    old_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    width: 960px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 32px !important;
    left: 270px !important;
    width: 960px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)

    # Add topbar cleanup overrides under landscape media query block
    topbar_landscape_override = """  /* 最上排按鈕與工具列整齊美化樣式 */
  .topbar-grouped-v9 {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    gap: 12px !important;
    background: linear-gradient(180deg, rgba(20, 15, 30, 0.96) 0%, rgba(10, 8, 18, 0.98) 100%) !important;
    border-bottom: 1.5px solid rgba(212, 175, 55, 0.5) !important;
    height: 38px !important;
  }
  .topbar-group {
    background: rgba(0, 0, 0, 0.5) !important;
    border: 1px solid rgba(212, 175, 55, 0.25) !important;
    border-radius: 8px !important;
    padding: 3px 8px !important;
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
  }
  .topbar-group select,
  .topbar-setting-btn,
  .topbar-action-btn {
    height: 28px !important;
    font-size: 13px !important;
    padding: 2px 8px !important;
    border-radius: 6px !important;
    border: 1px solid rgba(212, 175, 55, 0.4) !important;
    background: rgba(20, 16, 32, 0.8) !important;
    color: #ffffff !important;
    font-weight: bold !important;
  }
  .topbar-group select:hover,
  .topbar-setting-btn:hover,
  .topbar-action-btn:hover {
    border-color: #ffd76a !important;
    background: rgba(40, 30, 60, 0.9) !important;
  }"""

    # Insert topbar overrides inside the media query
    css_content = css_content.replace(
        "  /* 2. 對戰棋盤放大為 scale(0.45) 絕對置中，極大化戰場視野 */",
        topbar_landscape_override + "\n\n  /* 2. 對戰棋盤放大為 scale(0.45) 絕對置中，極大化戰場視野 */"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Repositioned panels and aligned topbar button styles in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.30-hud-realignment-done
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.30-hud-realignment-done', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.30-hud-realignment-done', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    hud_restyle_and_topbar_neat()
