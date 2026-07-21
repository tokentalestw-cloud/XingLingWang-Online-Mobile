# -*- coding: utf-8 -*-
import sys, re

def fix_full_layout_scale():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    uniform_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (48% 全版面均勻縮放，完整呈現所有系統與區域)
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
  margin: 10px auto !important;
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

/* 48% 全版面整體縮放 (包含最上排工具列、敵方區域、中央戰場、我方區域與操作按鈕 100% 全露出) */
body.xlw-iphone14-sim-active .board-wrap {
  width: 100% !important;
  height: 100% !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}

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

/* 頂部工具列 (Top Bar) 46% 縮放定位於 iPhone 14 內部正上方 */
body.xlw-iphone14-sim-active .topbar-grouped-v9 {
  position: absolute !important;
  top: 8px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.68) !important;
  transform-origin: top center !important;
  z-index: 10020 !important;
  background: rgba(12, 8, 20, 0.96) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(212, 175, 55, 0.5) !important;
  width: auto !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8) !important;
}

/* 右下角操作按鈕面板 70% 獨立定位於右下角 */
body.xlw-iphone14-sim-active #stableActionPanel {
  position: absolute !important;
  right: 12px !important;
  bottom: 12px !important;
  top: auto !important;
  left: auto !important;
  z-index: 10000 !important;
  transform: scale(0.70) !important;
  transform-origin: bottom right !important;
  display: flex !important;
}

/* 中上方階段提示面板 70% 獨立定位於頂欄下方 */
body.xlw-iphone14-sim-active #phaseDisplayPanelHard {
  position: absolute !important;
  top: 48px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.70) !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 左上方對手狀態欄 70% 獨立定位於左上角 */
body.xlw-iphone14-sim-active #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 48px !important;
  left: 12px !important;
  z-index: 10000 !important;
  transform: scale(0.70) !important;
  transform-origin: top left !important;
}

/* 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .xlw-left-card-panel,
body.xlw-iphone14-sim-active #xlwLeftCardPanel {
  position: absolute !important;
  left: 8px !important;
  bottom: 8px !important;
  top: auto !important;
  z-index: 10050 !important;
  transform: scale(0.70) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += uniform_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with 100% full-system layout scaling successfully!")

    # Update cache-buster in static/index.html to v=14.30-iphone14-full-system-perfect-fit
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.30-iphone14-full-system-perfect-fit', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.30-iphone14-full-system-perfect-fit', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_full_layout_scale()
