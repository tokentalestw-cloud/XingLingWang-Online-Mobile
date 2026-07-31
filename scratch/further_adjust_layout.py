# -*- coding: utf-8 -*-
import sys, re

def further_adjust():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Shift boardWrap X translation to -42.5% (halfway between -50% and -35%)
    css_content = css_content.replace(
        "transform: translate(-35%, -50%) scale(0.46) !important;",
        "transform: translate(-42.5%, -50%) scale(0.46) !important;"
    )

    # 2. Correct playerExile top coordinate from 467.5px (middle row) to 781.5px (bottom row next to deck)
    css_content = css_content.replace(
        "#playerExile { right: 330px !important; top: 467.5px !important; }",
        "#playerExile { right: 330px !important; top: 781.5px !important; }"
    )

    # 3. Double preview panel scale to 1.30 and position it very close to screen edge (left: -15px, bottom: 4px)
    old_preview = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: 8px !important;
    bottom: 8px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }"""

    new_preview = """  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    left: -15px !important;
    bottom: 4px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(1.30) !important;
    transform-origin: bottom left !important;
  }"""

    css_content = css_content.replace(old_preview, new_preview)

    # 4. Double status panels scale to 0.72 and adjust enemy panel top to 140px to prevent overlap
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
    transform: scale(0.36) !important;
    transform-origin: top left !important;
    width: 230px !important;
    height: auto !important;
    margin: 0 !important;
  }"""

    new_score_badge = """  #scoreBadgeFixed {
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

    css_content = css_content.replace(old_score_badge, new_score_badge)

    old_enemy_panel = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 8px !important;
    top: 100px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.36) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 230px !important;
  }"""

    new_enemy_panel = """  #xlwEnemyInfoPanel {
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

    css_content = css_content.replace(old_enemy_panel, new_enemy_panel)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Successfully shifted boardWrap, aligned playerExile, and doubled preview & status scale in style_v8.css!")

    # 5. Update cache-buster in static/index.html to v=18.90-layout-final-balanced
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.90-layout-final-balanced', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.90-layout-final-balanced', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    further_adjust()
