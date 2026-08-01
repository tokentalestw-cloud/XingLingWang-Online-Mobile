# -*- coding: utf-8 -*-
import sys, re

def align_playmats_and_halve():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update renderEnemyPanel in static/game_v8.js to be ultra-compact (width 55px friendly)
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
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important;">👾 對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
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
    <div class="enemy-info-title" style="text-align: center; font-size: 11px !important; white-space: nowrap;">👾手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 0 !important; margin: 0 !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Made renderEnemyPanel ultra-compact in game_v8.js successfully!")

    # 2. Modify static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Move #xlwEnemyInfoPanel to top: 32px, left: 180px, width: 55px, padding: 2px 4px
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
    padding: 2px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Restyle boardWrap to be transparent with no border/shadow
    old_board_style = """  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 30% !important;
    left: 50% !important;
    transform: translate(-42.5%, -50%) scale(0.46) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }"""

    new_board_style = """  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 30% !important;
    left: 50% !important;
    transform: translate(-42.5%, -50%) scale(0.46) !important;
    transform-origin: center center !important;
    margin: 0 !important;
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
  }"""

    css_content = css_content.replace(old_board_style, new_board_style)

    # Move playmats downward and add the gold border and shadow directly onto them
    old_playmats_style = """  /* 調整卡墊背景圖向左下方移動與格子對齊 */
  .board::before {
    left: -90px !important;
    right: 330px !important;
    height: 47% !important;
  }
  .board::after {
    left: -90px !important;
    right: 330px !important;
    height: 47% !important;
  }"""

    new_playmats_style = """  /* 調整卡墊背景圖與外框向左下方移動與格子對齊 */
  .board::before {
    left: -90px !important;
    right: 330px !important;
    top: 140px !important;
    height: 310px !important;
    border: 1.5px solid rgba(255, 215, 106, 0.35) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
  }
  .board::after {
    left: -90px !important;
    right: 330px !important;
    top: 610px !important;
    height: 315px !important;
    border: 1.5px solid rgba(255, 215, 106, 0.35) !important;
    border-radius: 16px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
  }"""

    css_content = css_content.replace(old_playmats_style, new_playmats_style)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Repositioned playmats and added outer borders directly in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.60-playmats-perfected
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.60-playmats-perfected', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.60-playmats-perfected', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    align_playmats_and_halve()
