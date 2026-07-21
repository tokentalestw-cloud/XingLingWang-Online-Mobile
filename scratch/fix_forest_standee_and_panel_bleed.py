# -*- coding: utf-8 -*-
import sys, re

def fix_standee_and_bleed():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Restore traveler-3d-standee in static/index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Re-insert standees into enemyForest and playerForest if missing
    enemy_forest_pattern = r'<div id="enemyForest" class="zone side green">\s*<div class="forest-3d-wrap">\s*<div class="forest-3d-bg"></div>\s*<div class="forest-3d-trees"></div>'
    enemy_forest_replacement = """<div id="enemyForest" class="zone side green">
          <div class="forest-3d-wrap">
            <div class="forest-3d-bg"></div>
            <div class="forest-3d-trees"></div>
            <div class="traveler-3d-standee">
              <img src="/static/little_traveler.jpeg" class="traveler-3d-img" alt="小旅人">
            </div>"""

    player_forest_pattern = r'<div id="playerForest" class="zone side green" onclick="triggerLittleTraveler\(event\)">\s*<div class="forest-3d-wrap">\s*<div class="forest-3d-bg"></div>\s*<div class="forest-3d-trees"></div>'
    player_forest_replacement = """<div id="playerForest" class="zone side green" onclick="triggerLittleTraveler(event)">
          <div class="forest-3d-wrap">
            <div class="forest-3d-bg"></div>
            <div class="forest-3d-trees"></div>
            <div class="traveler-3d-standee">
              <img src="/static/little_traveler.jpeg" class="traveler-3d-img" alt="小旅人">
            </div>"""

    if "traveler-3d-standee" not in idx_content:
        idx_content = re.sub(enemy_forest_pattern, enemy_forest_replacement, idx_content)
        idx_content = re.sub(player_forest_pattern, player_forest_replacement, idx_content)
        print("1. Restored traveler-3d-standee in static/index.html!")

    # Update cache-buster to v=9.60-standee-restored-bleed-fixed
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.60-standee-restored-bleed-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.60-standee-restored-bleed-fixed', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)

    # 2. Append CSS containment and opacity fixes to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    new_css = """

/* ==========================================================================
   FOREST STANDEE CONTAINMENT & LEFT PANEL OPACITY FIX
   (確保森林區小旅人精緻防護，且絕不重疊透出左側卡牌放大視窗)
   ========================================================================== */

#playerForest, #enemyForest {
  overflow: hidden !important;
}

.traveler-3d-standee {
  width: 58px !important;
  height: 80px !important;
  position: absolute !important;
  bottom: 8px !important;
  left: 50% !important;
  transform: translateX(-50%) translateZ(10px) rotateX(-5deg) !important;
  pointer-events: none !important;
  z-index: 2 !important;
}

.xlw-left-card-panel {
  background: #0c080e !important;
  z-index: 10050 !important;
  box-shadow: 0 12px 50px rgba(0, 0, 0, 0.98), 0 0 25px rgba(255, 230, 0, 0.4) !important;
}

.xlw-left-card-panel .panel-inner {
  position: relative !important;
  z-index: 2 !important;
  background: #0c080e !important;
}

"""

    css_content += new_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended CSS containment & opacity fixes to static/style_v8.css successfully!")

if __name__ == '__main__':
    fix_standee_and_bleed()
