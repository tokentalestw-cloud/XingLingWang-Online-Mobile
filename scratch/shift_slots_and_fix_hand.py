# -*- coding: utf-8 -*-
import sys, re

def shift_and_fix():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Update global positioning of right-side zones to shift them left by 420px (from right: 34px to right: 454px)
    old_positions = """#enemyField { right: 34px !important; top: 301.5px !important; } /* Swapped to bottom */
#enemyForest { right: 34px !important; top: 155.5px !important; } /* Swapped to top */

#playerField { left: 34px !important; top: 627.5px !important; }
#playerForest { left: 34px !important; top: 781.5px !important; }

#playerGrave { right: 34px !important; top: 627.5px !important; }
#playerDeck { right: 34px !important; top: 781.5px !important; }
#playerRace { right: 34px !important; top: 467.5px !important; }
#playerExile { right: -90px !important; top: 467.5px !important; }"""

    new_positions = """#enemyField { right: 454px !important; top: 301.5px !important; } /* Swapped to bottom */
#enemyForest { right: 454px !important; top: 155.5px !important; } /* Swapped to top */

#playerField { left: 34px !important; top: 627.5px !important; }
#playerForest { left: 34px !important; top: 781.5px !important; }

#playerGrave { right: 454px !important; top: 627.5px !important; }
#playerDeck { right: 454px !important; top: 781.5px !important; }
#playerRace { right: 454px !important; top: 467.5px !important; }
#playerExile { right: 330px !important; top: 467.5px !important; }"""

    css_content = css_content.replace(old_positions, new_positions)

    # 2. Enlarge hand-panel and card sizes, and add override to .mini-meta for hand cards to make images visible
    old_hand_styles = """  .hand-panel {
    position: fixed !important;
    bottom: 14px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 520px !important; /* 固定寬度，防範 iOS Safari 寬度崩塌 */
    max-width: 90vw !important;
    height: 80px !important;
    min-height: 80px !important;
    max-height: 80px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    display: flex !important;
    align-items: flex-end !important;
    overflow: visible !important;
    z-index: 10010 !important;
    margin: 0 !important;
    padding: 0 !important;
  }"""

    new_hand_styles = """  .hand-panel {
    position: fixed !important;
    bottom: 4px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 650px !important; /* 固定寬度，防範 iOS Safari 寬度崩塌 */
    max-width: 90vw !important;
    height: 130px !important;
    min-height: 130px !important;
    max-height: 130px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    display: flex !important;
    align-items: flex-end !important;
    overflow: visible !important;
    z-index: 10010 !important;
    margin: 0 !important;
    padding: 0 !important;
  }"""

    css_content = css_content.replace(old_hand_styles, new_hand_styles)

    old_card_styles = """  .hand .card {
    width: 54px !important;
    height: 74px !important;
    min-width: 48px !important;
    flex: 0 0 54px !important;
    margin-left: -8px !important;
    border-radius: 4px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(15deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }"""

    new_card_styles = """  .hand .card {
    width: 80px !important;
    height: 110px !important;
    min-width: 60px !important;
    flex: 0 0 80px !important;
    margin-left: -15px !important;
    border-radius: 6px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(15deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }
  .hand .card .mini-meta {
    font-size: 9px !important;
    line-height: 1.2 !important;
    padding: 3px 2px !important;
    background: rgba(8, 6, 12, 0.85) !important;
  }"""

    css_content = css_content.replace(old_card_styles, new_card_styles)

    # Update translateY on hover
    css_content = css_content.replace(
        "transform: perspective(300px) rotateX(0deg) translateY(-24px) scale(1.4) !important;",
        "transform: perspective(300px) rotateX(0deg) translateY(-35px) scale(1.4) !important;"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Shifted right-side slots and updated hand card styles in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=18.50-shifted-and-hand-enlarged
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.50-shifted-and-hand-enlarged', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.50-shifted-and-hand-enlarged', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    shift_and_fix()
