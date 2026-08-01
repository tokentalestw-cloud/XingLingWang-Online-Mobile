# -*- coding: utf-8 -*-
import sys, re

def fix_rotation_and_hand():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update renderEnemyPanel in static/game_v8.js to single-line & 0.5px border
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
    <div class="enemy-info-title" style="text-align: center; font-size: 14px !important; font-weight: bold; line-height: 1.15; color: #ffd76a;">對手<br>手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 17px !important; font-weight: bold; color: #ff7875 !important; padding: 0 !important; margin: 0 !important; white-space: nowrap;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
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
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important; white-space: nowrap; font-weight: bold; color: #ffd76a;">👾 對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important; padding: 2px 6px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.25) !important; border-radius: 4px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Restored single-line renderEnemyPanel in game_v8.js successfully!")

    # 2. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Re-style #xlwEnemyInfoPanel in style_v8.css landscape block
    old_enemy_style = """  #xlwEnemyInfoPanel {
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
    padding: 6px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
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
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Enhance the @media (orientation: portrait) block to force wrapper dimensions
    old_lock_block = """/* ===== 完美強制橫向螢幕鎖定 (Physical Orientation Lock to Landscape) ===== */
@media (orientation: portrait) {
  html {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    position: fixed !important;
  }
  body {
    width: 100vh !important;
    height: 100vw !important;
    position: fixed !important;
    top: 0 !important;
    left: 100vw !important;
    transform: rotate(90deg) !important;
    transform-origin: top left !important;
    overflow: hidden !important;
  }
}"""

    new_lock_block = """/* ===== 完美強制橫向螢幕鎖定 (Physical Orientation Lock to Landscape) ===== */
@media (orientation: portrait) {
  html {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    position: fixed !important;
  }
  body {
    width: 100vh !important;
    height: 100vw !important;
    position: fixed !important;
    top: 0 !important;
    left: 100vw !important;
    transform: rotate(90deg) !important;
    transform-origin: top left !important;
    overflow: hidden !important;
  }
  /* Force all wrappers to occupy the full rotated space of the body */
  .game-shell,
  .board-wrap,
  .xlw-welcome-overlay {
    width: 100% !important;
    height: 100% !important;
  }
}"""

    css_content = css_content.replace(old_lock_block, new_lock_block)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated xlwEnemyInfoPanel and locked wrappers under rotation in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.95-landscape-lock-stabilized
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.95-landscape-lock-stabilized', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.95-landscape-lock-stabilized', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_rotation_and_hand()
