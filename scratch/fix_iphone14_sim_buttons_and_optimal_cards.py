# -*- coding: utf-8 -*-
import sys, re

def fix_iphone14_buttons_and_cards():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    perfect_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (按鈕完整呈現在內 + 最適卡牌清晰度 62% 縮放)
   ========================================================================== */

body.xlw-iphone14-sim-active {
  background: radial-gradient(circle at 50% 50%, #1c152a 0%, #07050a 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
}

body.xlw-iphone14-sim-active .game-shell {
  width: 844px !important;
  height: 390px !important;
  min-width: 844px !important;
  min-height: 390px !important;
  max-width: 844px !important;
  max-height: 390px !important;
  margin: 14px auto !important;
  box-sizing: content-box !important;
  border-radius: 44px !important;
  border: 14px solid #1c1c1e !important;
  outline: 2px solid #2c2c2e !important;
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.95),
    0 0 35px rgba(255, 215, 106, 0.3) !important;
  overflow: hidden !important;
  position: relative !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 1. 最適卡牌放大與戰場清晰度 (62% 精準比例，文字清晰且無溢出) */
body.xlw-iphone14-sim-active .board-wrap,
body.xlw-iphone14-sim-active #boardWrap {
  zoom: 0.62 !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.62) {
  body.xlw-iphone14-sim-active .board-wrap,
  body.xlw-iphone14-sim-active #boardWrap {
    transform: scale(0.62) !important;
    transform-origin: center center !important;
  }
}

/* 2. 右下角操作按鈕面板完整定位於 iPhone 14 模擬器內部 */
body.xlw-iphone14-sim-active #stableActionPanel {
  position: absolute !important;
  right: 14px !important;
  bottom: 14px !important;
  top: auto !important;
  left: auto !important;
  z-index: 10000 !important;
  transform: scale(0.82) !important;
  transform-origin: bottom right !important;
  display: flex !important;
}

/* 3. 中上方階段提示面板完整定位於 iPhone 14 模擬器內部 */
body.xlw-iphone14-sim-active #phaseDisplayPanelHard {
  position: absolute !important;
  top: 10px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.82) !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 4. 左上方對手狀態欄完整定位於 iPhone 14 模擬器內部 */
body.xlw-iphone14-sim-active #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 10px !important;
  left: 14px !important;
  z-index: 10000 !important;
  transform: scale(0.82) !important;
  transform-origin: top left !important;
}

/* 5. 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .xlw-left-card-panel,
body.xlw-iphone14-sim-active #xlwLeftCardPanel {
  position: absolute !important;
  left: 10px !important;
  bottom: 10px !important;
  top: auto !important;
  z-index: 10050 !important;
  transform: scale(0.85) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += perfect_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with repositioned action buttons and optimal 62% card zoom successfully!")

    # Update cache-buster in static/index.html to v=14.00-iphone14-buttons-and-optimal-cards
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.00-iphone14-buttons-and-optimal-cards', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.00-iphone14-buttons-and-optimal-cards', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_iphone14_buttons_and_cards()
