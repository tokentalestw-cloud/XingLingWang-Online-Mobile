# -*- coding: utf-8 -*-
import sys, re

def fix_major_upward_shift():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    major_shift_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (工具列 0.46 大幅縮放不溢出 + 棋盤大幅上移 -55px 完美居中)
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

/* 1. 工具列 (Top Bar) 0.46 大幅精確縮放，全數 10 個按鈕 100% 完全收納於 844px 內部，右側留白絕不溢出 */
body.xlw-iphone14-sim-active .game-shell .topbar-grouped-v9 {
  position: absolute !important;
  top: 4px !important;
  left: 4px !important;
  width: 1350px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 4px !important;
  margin: 0 !important;
  transform: scale(0.46) !important;
  transform-origin: top left !important;
  z-index: 10020 !important;
  background: rgba(12, 8, 20, 0.96) !important;
  border: 1px solid rgba(212, 175, 55, 0.5) !important;
  border-radius: 8px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
}

/* 2. 對戰棋盤大幅向上拉升 55px (-55px margin-top)，敵我雙方區域與手牌全數垂直置中 */
body.xlw-iphone14-sim-active .game-shell .board-wrap {
  width: 100% !important;
  height: 390px !important;
  margin-top: -55px !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}

body.xlw-iphone14-sim-active .game-shell #boardWrap {
  zoom: 0.42 !important;
  margin: 0 auto !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.42) {
  body.xlw-iphone14-sim-active .game-shell #boardWrap {
    transform: scale(0.42) !important;
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

/* 4. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列右側下方 */
body.xlw-iphone14-sim-active .game-shell #phaseDisplayPanelHard {
  position: absolute !important;
  top: 22px !important;
  left: 450px !important;
  transform: scale(0.58) !important;
  transform-origin: top left !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 5. 左上方對手狀態欄 (#xlwEnemyInfoPanel) 定位於工具列下方左側 */
body.xlw-iphone14-sim-active .game-shell #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 22px !important;
  left: 10px !important;
  transform: scale(0.58) !important;
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

    css_content += major_shift_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with major topbar scaling 0.46x and board upward shift -55px successfully!")

    # Update cache-buster in static/index.html to v=14.80-iphone14-major-upward-shift
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.80-iphone14-major-upward-shift', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.80-iphone14-major-upward-shift', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_major_upward_shift()
