# -*- coding: utf-8 -*-
import sys, re

def fix_orientation_queries():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # 1. Replace the legacy coarse pointer portrait queries to ONLY match portrait orientation
    css_content = css_content.replace(
        "@media (max-width: 900px) and (orientation: portrait), (pointer: coarse) and (max-width: 900px)",
        "@media (max-width: 1024px) and (orientation: portrait)"
    )

    # 2. Clean and replace the custom mobile RWD block at the bottom
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    landscape_rwd_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (實體手機橫向專屬黃金版面 - 解決 iOS zoom 屬性失效問題)
   ========================================================================== */

@media (max-width: 1024px) and (orientation: landscape) {
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
    border: none !important;
    box-shadow: none !important;
  }

  /* 1. 最上排工具列 (Top Bar) 0.46 大幅精確縮放，手機橫向 100% 完全收納，右側不溢出 */
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

  /* 2. 對戰棋盤使用 Safari 完整支援的 transform 進行絕對置中與 0.38 縮放，完全解決 iOS zoom 屬性失效問題 */
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
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -46%) scale(0.38) !important;
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

    css_content += landscape_rwd_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with orientation landscape RWD successfully!")

    # Update cache-buster in static/index.html to v=15.40-ios-landscape-orientation-fixed
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.40-ios-landscape-orientation-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.40-ios-landscape-orientation-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_orientation_queries()
