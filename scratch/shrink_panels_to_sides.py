# -*- coding: utf-8 -*-
import sys, re

def shrink_to_sides():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Clean old Master Duel css priority blocks to avoid duplicate style blocks
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    sides_shrunk_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (左右面板極致縮小、緊貼邊緣、戰場極大化)
   ========================================================================== */

@media (max-width: 1024px) and (orientation: landscape) {
  html, body {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    display: block !important;
  }

  /* 遊戲外殼滿版佔領 100% 畫面 */
  .game-shell {
    width: 100vw !important;
    height: 100vh !important;
    min-height: 100vh !important;
    max-height: 100vh !important;
    position: relative !important;
    overflow: hidden !important;
    display: block !important;
    background: #070505 !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* 1. 最上排工具列 (Top Bar) 0.32 大幅微縮，完全收納於頂部，不擋戰線 */
  .topbar-grouped-v9 {
    position: absolute !important;
    top: 2px !important;
    left: 2px !important;
    width: 1480px !important;
    max-width: 1480px !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 4px !important;
    margin: 0 !important;
    transform: scale(0.32) !important;
    transform-origin: top left !important;
    z-index: 10020 !important;
    background: rgba(12, 8, 20, 0.96) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
  }

  /* 2. 對戰棋盤放大為 scale(0.45) 絕對置中，極大化戰場視野 */
  .board-wrap {
    width: 100% !important;
    height: 100% !important;
    position: relative !important;
    overflow: visible !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  #boardWrap {
    width: 1400px !important;
    height: 760px !important;
    min-width: 1400px !important;
    min-height: 760px !important;
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) scale(0.45) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }

  /* 3. 雙方分數看板 (#scoreBadgeFixed) 縮至最小並靠最左邊，縮放為 36% */
  #scoreBadgeFixed {
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
  }
  
  .score-badge-section {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
  }

  .score-badge-card {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .score-badge-label {
    font-size: 12px !important;
    color: #ffd76a !important;
  }

  .score-badge-num {
    font-size: 15px !important;
    font-weight: bold !important;
    color: #ffffff !important;
  }

  .score-badge-subrow {
    font-size: 10px !important;
    opacity: 0.85 !important;
  }

  /* 4. 對手狀態欄 (#xlwEnemyInfoPanel) 縮至最小並靠最左邊，縮放為 36% */
  #xlwEnemyInfoPanel {
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
  }

  /* 5. 右側操作按鈕面板 (#stableActionPanel) 縮至最小並靠最右邊，縮放為 30% (確認換牌、重置新局等) */
  #stableActionPanel {
    position: absolute !important;
    right: 8px !important;
    bottom: 12px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.30) !important;
    transform-origin: bottom right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 6px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.7) !important;
    margin: 0 !important;
    width: 120px !important;
  }

  #stableActionPanel .stable-action-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
  }

  #stableActionPanel .stable-action-btn {
    width: 100% !important;
    font-size: 12px !important;
    padding: 6px 8px !important;
    border-radius: 50px !important;
    border: 1.5px solid #ffd76a !important;
    box-shadow: 0 0 6px rgba(255, 215, 106, 0.3) !important;
    white-space: nowrap !important;
  }

  /* 6. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方中軸 */
  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }

  /* 7. 懸浮 3D 立體我方手牌區 (釘死於視窗底部，高度 80px，100% 可見) */
  .hand-panel {
    position: fixed !important;
    bottom: 14px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: auto !important;
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
  }

  /* 拿掉「我方手牌」文字標題 */
  .hand-title {
    display: none !important;
  }

  .hand {
    flex: 1 !important;
    height: 100% !important;
    padding: 0 10px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: flex-end !important;
    gap: 3px !important;
    overflow: visible !important;
  }

  /* 3D 視角立體斜度手牌 (54px x 74px) */
  .hand .card {
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
  }

  .hand .card:first-child {
    margin-left: 0 !important;
  }

  /* 手牌 Hover/Touch 浮空拉起 24px 並放大 1.4 倍 */
  .hand .card:hover,
  .hand .card:active {
    z-index: 200 !important;
    transform: perspective(300px) rotateX(0deg) translateY(-24px) scale(1.4) !important;
    box-shadow: 0 12px 25px rgba(0, 0, 0, 0.85), 0 0 10px rgba(255, 215, 106, 0.3) !important;
  }

  /* 左側卡牌放大預覽面板獨立彈出適配 */
  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: absolute !important;
    left: 8px !important;
    bottom: 95px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }
}

"""

    css_content += sides_shrunk_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated static/style_v8.css with shrunken side panels successfully!")

    # Update cache-buster in static/index.html to v=17.40-sides-panels-shrunked
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.40-sides-panels-shrunked', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.40-sides-panels-shrunked', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    shrink_to_sides()
