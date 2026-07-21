# -*- coding: utf-8 -*-
import sys, re

def fix_non_overlapping_layout():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    no_overlap_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (按鈕與對戰格子 0 重疊黃金排版 - 電腦版 0 影響)
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
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 1. 對戰棋盤向左微移，預留右側操作專區 (0 重疊) */
body.xlw-iphone14-sim-active .board-wrap {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  justify-content: flex-start !important;
  align-items: center !important;
  padding-left: 20px !important;
  position: relative !important;
}

body.xlw-iphone14-sim-active #boardWrap {
  zoom: 0.42 !important;
  margin: auto 0 auto 10px !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.42) {
  body.xlw-iphone14-sim-active #boardWrap {
    transform: scale(0.42) !important;
    transform-origin: center center !important;
  }
}

/* 2. 右側獨立對戰操作面板 (極簡垂直懸浮柱，絕不覆蓋任何對戰格子) */
body.xlw-iphone14-sim-active #stableActionPanel {
  position: fixed !important;
  left: calc(50vw + 422px - 148px) !important;
  top: 50% !important;
  transform: translateY(-50%) scale(0.70) !important;
  transform-origin: center right !important;
  right: auto !important;
  bottom: auto !important;
  z-index: 10000 !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  background: rgba(15, 10, 25, 0.92) !important;
  border: 1px solid rgba(255, 215, 106, 0.5) !important;
  border-radius: 14px !important;
  padding: 10px !important;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.85) !important;
}

body.xlw-iphone14-sim-active #stableActionPanel .stable-action-row {
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}

body.xlw-iphone14-sim-active #stableActionPanel .stable-action-btn {
  width: 130px !important;
  font-size: 14px !important;
  padding: 8px 10px !important;
  white-space: nowrap !important;
}

/* 3. 最上排工具列 (Top Bar) 定位於頂部 */
body.xlw-iphone14-sim-active .topbar-grouped-v9 {
  position: fixed !important;
  left: 50% !important;
  top: calc(50vh - 195px + 8px) !important;
  transform: translateX(-50%) scale(0.62) !important;
  transform-origin: top center !important;
  z-index: 10020 !important;
  background: rgba(12, 8, 20, 0.96) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(212, 175, 55, 0.5) !important;
  width: auto !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8) !important;
}

/* 4. 中上方階段提示面板鎖定頂欄下方 */
body.xlw-iphone14-sim-active #phaseDisplayPanelHard {
  position: fixed !important;
  left: 50% !important;
  top: calc(50vh - 195px + 45px) !important;
  transform: translateX(-50%) scale(0.68) !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 5. 左上方對手狀態欄鎖定左上角 */
body.xlw-iphone14-sim-active #xlwEnemyInfoPanel {
  position: fixed !important;
  left: calc(50vw - 422px + 16px) !important;
  top: calc(50vh - 195px + 45px) !important;
  z-index: 10000 !important;
  transform: scale(0.68) !important;
  transform-origin: top left !important;
  display: block !important;
}

/* 6. 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .xlw-left-card-panel,
body.xlw-iphone14-sim-active #xlwLeftCardPanel {
  position: fixed !important;
  left: calc(50vw - 422px + 12px) !important;
  top: calc(50vh + 195px - 340px) !important;
  z-index: 10050 !important;
  transform: scale(0.72) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += no_overlap_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with non-overlapping iPhone 14 simulator layout successfully!")

    # Update cache-buster in static/index.html to v=14.50-iphone14-non-overlapping-layout
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.50-iphone14-non-overlapping-layout', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.50-iphone14-non-overlapping-layout', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_non_overlapping_layout()
