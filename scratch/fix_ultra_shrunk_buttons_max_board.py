# -*- coding: utf-8 -*-
import sys, re

def fix_shrunk_buttons_max_board():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js adjustBoardScale for absolute maximum board scale 0.45
    js_content = open(js_path, encoding='utf-8').read()

    updated_adjust_scale_js = """// 實作動態自適應縮放引擎 (單螢幕無滾動佈局)
function adjustBoardScale() {
  const board = $("boardWrap");
  if (!board) return;

  const isMobile = window.matchMedia("(max-width: 900px), (pointer: coarse)").matches;
  const isPortraitMobile = window.matchMedia("(max-width: 900px) and (orientation: portrait), (pointer: coarse) and (max-width: 900px)").matches;
  const isLandscapeMobile = isMobile && !isPortraitMobile;

  const boardNaturalHeight = isPortraitMobile ? 920 : 940;
  const boardNaturalWidth = isPortraitMobile ? 760 : 980;

  let finalScale;
  if (isMobile) {
    if (isLandscapeMobile) {
      // 📱 橫向手機：最大化戰場 (0.45 比例置中，以高度貼合螢幕為準)
      finalScale = 0.45;
      document.documentElement.classList.add("xlw-mobile-layout");
      document.body.classList.add("xlw-mobile-layout");
    } else {
      // 📱 直向手機
      const safeSidePadding = 0;
      const availableWidth = Math.max(320, window.innerWidth - safeSidePadding);
      finalScale = Math.min((availableWidth / boardNaturalWidth), 0.94);
      document.documentElement.classList.add("xlw-mobile-layout");
      document.body.classList.add("xlw-mobile-layout");
    }
  } else {
    // 💻 電腦版
    const topbarH = 48;
    const handPanelH = 200;
    const padding = 16;
    const availableHeight = window.innerHeight - topbarH - handPanelH - padding;
    const availableWidth = window.innerWidth - 32;
    const scaleH = availableHeight / boardNaturalHeight;
    const scaleW = availableWidth / boardNaturalWidth;
    finalScale = Math.min(scaleH, scaleW, 1.0);
    document.documentElement.classList.remove("xlw-mobile-layout");
    document.body.classList.remove("xlw-mobile-layout");
  }

  // 設定 CSS 變數與縮放樣式
  document.documentElement.style.setProperty("--xlw-mobile-scale", String(finalScale));
  
  if (isMobile && isLandscapeMobile) {
    board.style.transform = `translate(-50%, -50%) scale(${finalScale})`;
    board.style.transformOrigin = "center center";
    board.style.position = "absolute";
    board.style.top = "50%";
    board.style.left = "50%";
    board.style.margin = "0";
  } else {
    board.style.transform = `scale(${finalScale})`;
    board.style.transformOrigin = "top center";
    board.style.position = "";
    board.style.top = "";
    board.style.left = "";
    board.style.margin = "0 auto";
  }

  const shell = document.querySelector(".game-shell");
  const wrap = document.querySelector(".board-wrap");

  if (isMobile && isLandscapeMobile) {
    if (shell) {
      shell.style.height = "100vh";
      shell.style.minHeight = "100vh";
    }
    if (wrap) {
      wrap.style.height = "100%";
      wrap.style.minHeight = "100%";
    }
  } else {
    if (shell) {
      const h = Math.ceil(boardNaturalHeight * finalScale);
      shell.style.height = `${h}px`;
      shell.style.minHeight = `${h}px`;
    }
    if (wrap) {
      const h = Math.ceil(boardNaturalHeight * finalScale);
      wrap.style.height = `${h}px`;
      wrap.style.minHeight = `${h}px`;
    }
  }
}"""

    # Replace adjustBoardScale in js
    start_marker = "function adjustBoardScale() {"
    idx = js_content.find(start_marker)
    if idx >= 0:
        brace_count = 0
        end_idx = idx
        for i in range(idx + len(start_marker), len(js_content)):
            if js_content[i] == '{':
                brace_count += 1
            elif js_content[i] == '}':
                if brace_count == 0:
                    end_idx = i + 1
                    break
                else:
                    brace_count -= 1
        js_content = js_content[:idx] + updated_adjust_scale_js + js_content[end_idx:]

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js scaling logic successfully!")

    # 2. Update static/style_v8.css with shrunken buttons and floating hand panel
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old Master Duel css priority blocks
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    ultra_shrunk_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (按鈕縮小至 1/3 以下、戰場極大化、手牌精確浮出)
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

  /* 1. 最上排工具列 (Top Bar) 0.33 大幅微縮，完全收納於頂部，不擋戰線 */
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

  /* 3. 我方得分看板 (圓形霓虹數字，直徑 38px) -> 靠左下角 */
  .score-badge-fixed.score-p1 {
    position: absolute !important;
    left: 12px !important;
    bottom: 12px !important;
    top: auto !important;
    right: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.88) !important;
    border: 2px solid #52c41a !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 0 12px rgba(82, 196, 26, 0.6) !important;
    transform: none !important;
    margin: 0 !important;
  }

  /* 4. 對手得分看板 (圓形霓虹數字，直徑 38px) -> 靠右上角 */
  .score-badge-fixed.score-p2 {
    position: absolute !important;
    right: 12px !important;
    top: 12px !important;
    left: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.88) !important;
    border: 2px solid #ff4d4f !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 0 12px rgba(255, 77, 79, 0.6) !important;
    transform: none !important;
    margin: 0 !important;
  }

  /* 隱藏標籤文字，僅顯示霓虹數字 */
  .score-badge-fixed .score-badge-label,
  .score-badge-fixed .score-badge-stars,
  .score-badge-fixed .score-badge-subrow {
    display: none !important;
  }
  .score-badge-fixed .score-badge-num {
    font-size: 13px !important;
    font-weight: 900 !important;
    color: #ffffff !important;
    margin: 0 !important;
    line-height: 1 !important;
  }

  /* 5. 對手狀態欄 (#xlwEnemyInfoPanel) 大幅微縮為 38% 並靠左側，分數板下方 */
  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 12px !important;
    top: 75px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.38) !important;
    transform-origin: top left !important;
    margin: 0 !important;
    display: block !important;
  }

  /* 6. 右側操作按鈕面板 (#stableActionPanel) 極致縮小為 0.30 倍 (低於 1/3)，完全不擋格子 */
  #stableActionPanel {
    position: absolute !important;
    right: 12px !important;
    bottom: 12px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.30) !important;
    transform-origin: bottom right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 6px !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  #stableActionPanel .stable-action-row {
    display: flex !important;
    flex-direction: column !important;
    gap: 5px !important;
  }

  #stableActionPanel .stable-action-btn {
    width: 100px !important;
    font-size: 12px !important;
    padding: 6px 8px !important;
    border-radius: 50px !important;
    border: 2px solid #ffd76a !important;
    box-shadow: 0 0 8px rgba(255, 215, 106, 0.4) !important;
    white-space: nowrap !important;
  }

  /* 7. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方中軸 */
  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }

  /* 8. 懸浮 3D 立體我方手牌區 (懸浮高度拉升至 bottom: 14px，保證在戰場之上 100% 完整露出) */
  .hand-panel {
    position: absolute !important;
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

  /* 3D 視角立體斜度手牌 (54px x 74px 精緻大小，絕對可見) */
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

    css_content += ultra_shrunk_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated static/style_v8.css with ultra shrunk buttons & max board successfully!")

    # Update cache-buster in static/index.html to v=16.20-shrunked-buttons-max-board
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=16.20-shrunked-buttons-max-board', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=16.20-shrunked-buttons-max-board', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_shrunk_buttons_max_board()
