# -*- coding: utf-8 -*-
import sys, re

def further_hud():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update renderEnemyPanel in static/game_v8.js to be ultra-compact
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

    # 2. Modify static/style_v8.css: Reposition panels
    css_content = open(css_path, encoding='utf-8').read()

    # Move #scoreBadgeFixed top to 110px
    old_score_badge = """  #scoreBadgeFixed {
    position: absolute !important;
    left: 8px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    width: 230px !important;
    height: auto !important;
    margin: 0 !important;
  }"""

    new_score_badge = """  #scoreBadgeFixed {
    position: absolute !important;
    left: 8px !important;
    top: 110px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    width: 230px !important;
    height: auto !important;
    margin: 0 !important;
  }"""

    css_content = css_content.replace(old_score_badge, new_score_badge)

    # Move #xlwEnemyInfoPanel to top: 110px, left: 180px, width: 55px
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
    top: 110px !important;
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

    # Shift #phaseDisplayPanelHard to the right by 25px (left: 295px)
    old_phase_style = """  #phaseDisplayPanelHard {
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

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 32px !important;
    left: 295px !important;
    width: 960px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Repositioned panels in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.40-hud-shift-completed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.40-hud-shift-completed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.40-hud-shift-completed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    further_hud()
