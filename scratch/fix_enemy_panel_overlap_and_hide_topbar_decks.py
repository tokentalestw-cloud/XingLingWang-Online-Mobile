# -*- coding: utf-8 -*-
import sys, re

def fix_overlap_and_hide_topbar():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Direct regex replacement for #xlwEnemyInfoPanel in the landscape media query
    old_enemy_pattern = r'#xlwEnemyInfoPanel\s*\{\s*position:\s*absolute\s*!important;\s*left:\s*180px\s*!important;\s*top:\s*32px\s*!important;'
    new_enemy_replacement = '#xlwEnemyInfoPanel {\n    position: absolute !important;\n    left: 8px !important;\n    top: 85px !important;'
    
    css_content, count = re.subn(old_enemy_pattern, new_enemy_replacement, css_content)
    print(f"Replaced #xlwEnemyInfoPanel left/top in CSS: {count} matches")

    # Add topbar deck group hiding style
    hide_topbar_decks_css = """
/* 隱藏最上排原生的陣營與牌組下拉選單 (已由 Pre-Battle Modal 取代) */
.topbar-group.deck-group {
  display: none !important;
}
"""
    css_content += hide_topbar_decks_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated style_v8.css to position #xlwEnemyInfoPanel at left: 8px, top: 85px and hide topbar deck dropdowns!")

    # 2. Update renderEnemyPanel in static/game_v8.js
    js_content = open(js_path, encoding='utf-8').read()

    old_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important; white-space: nowrap; font-weight: bold; color: #ffd76a;">👾 對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important; padding: 2px 6px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.25) !important; border-radius: 4px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
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
    <div class="enemy-info-title" style="text-align: center; font-size: 10px !important; white-space: nowrap; font-weight: bold; color: #ffd76a; line-height: 1;">對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 1px 4px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.2) !important; border-radius: 3px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated renderEnemyPanel in game_v8.js successfully!")

    # 3. Update static/index.html to add display: none to .deck-group and update cache-busters
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = idx_content.replace(
        '<div class="topbar-group deck-group">',
        '<div class="topbar-group deck-group" style="display: none !important;">'
    )

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.10-enemy-panel-repositioned-topbar-decks-hidden', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.10-enemy-panel-repositioned-topbar-decks-hidden', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated index.html to hide topbar deck dropdowns and updated cache-busters successfully!")

if __name__ == '__main__':
    fix_overlap_and_hide_topbar()
