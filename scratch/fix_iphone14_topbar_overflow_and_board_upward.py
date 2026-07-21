# -*- coding: utf-8 -*-
import sys, re

def fix_topbar_and_board_position():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    perfect_fit_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (工具列縮放不溢出 + 棋盤往上對齊完全居中)
   ========================================================================== */

body.xlw-iphone14-sim-active {
  background: radial-gradient(circle at 50% 50%, #1c152a 0%, #07050a 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  min-height: 100vh !important;
  overflow: hidden !important;
}

/* iPhone 14 實體機身邊框 (844px x 390px) */
body.xlw-iphone14-sim-active .game-shell {
  width: 844px !important;
  height: 390px !important;
  min-width: 844px !important;
  min-height: 390px !important;
  max-width: 844px !important;
  max-height: 390px !important;
  margin: 0 auto !important;
  box-sizing: content-box !important;
  border-radius: 44px !important;
  border: 14px solid #1c1c1e !important;
  outline: 2px solid #2c2c2e !important;
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.95),
    0 0 35px rgba(255, 215, 106, 0.3) !important;
  overflow: hidden !important;
  position: relative !important;
  display: block !important;
  background: #070505 !important;
}

/* 1. 最上排工具列 (Top Bar) 精準 0.56 縮放，100% 收納於 844px 寬度內部，右側按鈕絕不溢出 */
body.xlw-iphone14-sim-active .game-shell .topbar-grouped-v9 {
  position: absolute !important;
  top: 4px !important;
  left: 4px !important;
  width: 1480px !important;
  height: 34px !important;
  min-height: 34px !important;
  padding: 0 8px !important;
  margin: 0 !important;
  transform: scale(0.56) !important;
  transform-origin: top left !important;
  z-index: 10020 !important;
  background: rgba(12, 8, 20, 0.96) !important;
  border: 1px solid rgba(212, 175, 55, 0.5) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
}

/* 2. 對戰棋盤大幅往上移，垂直完美完全置中於 iPhone 14 視窗正中央 */
body.xlw-iphone14-sim-active .game-shell .board-wrap {
  width: 100% !important;
  height: 350px !important;
  margin-top: 24px !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}

body.xlw-iphone14-sim-active .game-shell #boardWrap {
  zoom: 0.44 !important;
  margin: 0 auto !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.44) {
  body.xlw-iphone14-sim-active .game-shell #boardWrap {
    transform: scale(0.44) !important;
    transform-origin: center center !important;
  }
}

/* 3. 右下角對戰操作按鈕面板 (#stableActionPanel) 獨立定位於 iPhone 14 內部右下角 */
body.xlw-iphone14-sim-active .game-shell #stableActionPanel {
  position: absolute !important;
  right: 10px !important;
  bottom: 10px !important;
  top: auto !important;
  left: auto !important;
  z-index: 10000 !important;
  transform: scale(0.68) !important;
  transform-origin: bottom right !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 5px !important;
  background: rgba(15, 10, 25, 0.92) !important;
  border: 1px solid rgba(255, 215, 106, 0.5) !important;
  border-radius: 12px !important;
  padding: 8px !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.85) !important;
}

body.xlw-iphone14-sim-active .game-shell #stableActionPanel .stable-action-row {
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
}

body.xlw-iphone14-sim-active .game-shell #stableActionPanel .stable-action-btn {
  width: 120px !important;
  font-size: 13px !important;
  padding: 6px 8px !important;
  white-space: nowrap !important;
}

/* 4. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方正中 */
body.xlw-iphone14-sim-active .game-shell #phaseDisplayPanelHard {
  position: absolute !important;
  top: 26px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.62) !important;
  transform-origin: top center !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 5. 左上方對手狀態欄 (#xlwEnemyInfoPanel) 定位於工具列下方左側 */
body.xlw-iphone14-sim-active .game-shell #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 26px !important;
  left: 10px !important;
  transform: scale(0.62) !important;
  transform-origin: top left !important;
  z-index: 10000 !important;
  display: block !important;
}

/* 6. 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .game-shell .xlw-left-card-panel,
body.xlw-iphone14-sim-active .game-shell #xlwLeftCardPanel {
  position: absolute !important;
  left: 10px !important;
  bottom: 10px !important;
  top: auto !important;
  z-index: 10050 !important;
  transform: scale(0.70) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += perfect_fit_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with topbar scaling and board upward centering successfully!")

    # Update cache-buster in static/index.html to v=14.70-iphone14-topbar-fit-board-upward
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.70-iphone14-topbar-fit-board-upward', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.70-iphone14-topbar-fit-board-upward', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_topbar_and_board_position()
