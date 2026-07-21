# -*- coding: utf-8 -*-
import sys, re

def fix_ios_scale_primary():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old mobile RWD CSS block at the bottom
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    real_mobile_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (100% iOS Safari 支援之 transform 絕對置中版面)
   ========================================================================== */

@media (max-width: 1024px) {
  html, body {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .game-shell {
    width: 100vw !important;
    height: 100vh !important;
    position: relative !important;
    overflow: hidden !important;
    display: block !important;
    background: #070505 !important;
  }

  /* 1. 最上排工具列 (Top Bar) 0.46 大幅精確縮放，全數 10 個按鈕 100% 收納於頂部 */
  .topbar-grouped-v9 {
    position: absolute !important;
    top: 2px !important;
    left: 2px !important;
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

  /* 2. 對戰棋盤使用 Safari 完整支援的 transform 進行絕對置中與 0.40 縮放，完全解決 iOS zoom 屬性失效問題 */
  .board-wrap {
    width: 100% !important;
    height: 100% !important;
    position: relative !important;
    overflow: visible !important;
  }

  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 52% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(0.40) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }

  /* 3. 右下角對戰操作按鈕面板 (#stableActionPanel) 精緻小型化收納於右下角 (絕不遮擋卡牌) */
  #stableActionPanel {
    position: absolute !important;
    right: 8px !important;
    bottom: 8px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.62) !important;
    transform-origin: bottom right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    background: rgba(15, 10, 25, 0.92) !important;
    border: 1px solid rgba(255, 215, 106, 0.5) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.85) !important;
  }

  #stableActionPanel .stable-action-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
  }

  #stableActionPanel .stable-action-btn {
    width: 115px !important;
    font-size: 13px !important;
    padding: 6px 8px !important;
    white-space: nowrap !important;
  }

  /* 4. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方中軸 */
  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 440px !important;
    transform: scale(0.54) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }

  /* 5. 左上方對手狀態欄 (#xlwEnemyInfoPanel) 定位於工具列下方左側 */
  #xlwEnemyInfoPanel {
    position: absolute !important;
    top: 20px !important;
    left: 8px !important;
    transform: scale(0.54) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: block !important;
  }

  /* 6. 左側卡牌放大預覽面板獨立彈出適配 */
  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: absolute !important;
    left: 8px !important;
    bottom: 8px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }
}

"""

    css_content += real_mobile_css
    
    # Also clean and update body.xlw-iphone14-sim-active to use absolute translate scale
    css_content = css_content.replace(
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  zoom: 0.42 !important;\n  margin: 0 auto !important;\n  transform-origin: center center !important;\n}",
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  width: 1400px !important;\n  height: 760px !important;\n  min-width: 1400px !important;\n  min-height: 760px !important;\n  position: absolute !important;\n  top: 52% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.40) !important;\n  transform-origin: center center !important;\n}"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with iOS absolute transform centering successfully!")

    # Update cache-buster in static/index.html to v=15.30-ios-transform-absolute-scale
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.30-ios-transform-absolute-scale', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.30-ios-transform-absolute-scale', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_ios_scale_primary()
