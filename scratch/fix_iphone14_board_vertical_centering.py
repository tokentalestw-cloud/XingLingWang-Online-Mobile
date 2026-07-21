# -*- coding: utf-8 -*-
import sys, re

def fix_vertical_centering():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    fit_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (44% 縮放垂直完美居中，敵方與我方區域全露出)
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

body.xlw-iphone14-sim-active .board-wrap {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}

/* 44% 縮放與完全垂直置中，確保敵方頂部牌庫與手牌全數在邊界內 */
body.xlw-iphone14-sim-active #boardWrap {
  zoom: 0.44 !important;
  margin: auto !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.44) {
  body.xlw-iphone14-sim-active #boardWrap {
    transform: scale(0.44) !important;
    transform-origin: center center !important;
  }
}

/* 右下角操作按鈕面板獨立定位 */
body.xlw-iphone14-sim-active #stableActionPanel {
  position: absolute !important;
  right: 14px !important;
  bottom: 14px !important;
  top: auto !important;
  left: auto !important;
  z-index: 10000 !important;
  transform: scale(0.78) !important;
  transform-origin: bottom right !important;
  display: flex !important;
}

/* 中上方階段提示面板獨立定位 */
body.xlw-iphone14-sim-active #phaseDisplayPanelHard {
  position: absolute !important;
  top: 10px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.78) !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 左上方對手狀態欄獨立定位 */
body.xlw-iphone14-sim-active #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 10px !important;
  left: 14px !important;
  z-index: 10000 !important;
  transform: scale(0.78) !important;
  transform-origin: top left !important;
}

/* 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .xlw-left-card-panel,
body.xlw-iphone14-sim-active #xlwLeftCardPanel {
  position: absolute !important;
  left: 10px !important;
  bottom: 10px !important;
  top: auto !important;
  z-index: 10050 !important;
  transform: scale(0.8) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += fit_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with 44% centered board zoom successfully!")

    # Update cache-buster in static/index.html to v=14.10-iphone14-enemy-fit-centered
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.10-iphone14-enemy-fit-centered', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.10-iphone14-enemy-fit-centered', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_vertical_centering()
