# -*- coding: utf-8 -*-
import sys, re

def lock_js_and_halve():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Force isPortraitMobile = false in static/game_v8.js
    js_content = open(js_path, encoding='utf-8').read()

    old_portrait_check = """  const isPortraitMobile = window.matchMedia("(max-width: 900px) and (orientation: portrait), (pointer: coarse) and (max-width: 900px)").matches;"""
    new_portrait_check = """  const isPortraitMobile = false; // Forced to false to prevent portrait scaling recalculations and layout jumping on physical rotation"""

    js_content = js_content.replace(old_portrait_check, new_portrait_check)

    # 2. Update renderEnemyPanel in static/game_v8.js
    old_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 11px !important; white-space: nowrap;">👾手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 0 !important; margin: 0 !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
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
    <div class="enemy-info-title" style="text-align: center; font-size: 14px !important; font-weight: bold; line-height: 1.15; color: #ffd76a;">對手<br>手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 17px !important; font-weight: bold; color: #ff7875 !important; padding: 0 !important; margin: 0 !important; white-space: nowrap;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Replaced isPortraitMobile and updated renderEnemyPanel in game_v8.js successfully!")

    # 3. Update style_v8.css: set width to 55px, padding to 6px 4px for xlwEnemyInfoPanel
    css_content = open(css_path, encoding='utf-8').read()

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
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
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
    padding: 6px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Repositioned and resized xlwEnemyInfoPanel in style_v8.css successfully!")

    # 4. Update cache-buster in static/index.html to v=19.90-no-jumping-on-rotation
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.90-no-jumping-on-rotation', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.90-no-jumping-on-rotation', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    lock_js_and_halve()
