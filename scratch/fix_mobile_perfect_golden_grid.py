# -*- coding: utf-8 -*-
import sys, re

def fix_golden_grid():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js adjustBoardScale to respect the golden grid heights
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
      // 📱 橫向手機黃金版面：以高度適配為基準，縮放設為 0.36 確保不重疊
      finalScale = 0.36;
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
      shell.style.height = "calc(100vh - 123px)";
      shell.style.minHeight = "calc(100vh - 123px)";
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

    # 2. Update static/style_v8.css with the perfect non-overlapping landscape CSS
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old mobile RWD CSS block at the bottom
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    golden_grid_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (黃金佈局：面板兩側縮放靠邊、手牌底部滿版露出)
   ========================================================================== */

@media (max-width: 1024px) and (orientation: landscape) {
  html, body {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    flex-direction: column !important;
  }

  /* 核心遊戲外殼夾在中間，保留底部手牌高度 */
  .game-shell {
    width: 100vw !important;
    height: calc(100vh - 95px) !important;
    min-height: calc(100vh - 95px) !important;
    max-height: calc(100vh - 95px) !important;
    position: relative !important;
    overflow: hidden !important;
    display: block !important;
    background: #070505 !important;
    border: none !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  /* 1. 最上排工具列 (Top Bar) 0.44 大幅微縮，100% 收納於頂部 */
  .topbar-grouped-v9 {
    position: absolute !important;
    top: 2px !important;
    left: 2px !important;
    width: 1480px !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 4px !important;
    margin: 0 !important;
    transform: scale(0.44) !important;
    transform-origin: top left !important;
    z-index: 10020 !important;
    background: rgba(12, 8, 20, 0.96) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
  }

  /* 2. 對戰棋盤使用 scale(0.36) 置中定位，保證左右兩側留出空間放置面板，0% 重疊 */
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
    transform: translate(-50%, -50%) scale(0.36) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }

  /* 3. 雙方總分面板 (.score-badge-fixed) 縮小為 50% 並靠最左上角 */
  .score-badge-fixed {
    position: absolute !important;
    left: 6px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    margin: 0 !important;
  }

  /* 4. 對手狀態欄 (#xlwEnemyInfoPanel) 縮小為 50% 並靠左側，緊鄰分數下方 */
  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 6px !important;
    top: 115px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    margin: 0 !important;
    display: block !important;
  }

  /* 5. 右側操作按鈕面板 (#stableActionPanel) 縮小為 0.54 並靠最右側置中 */
  #stableActionPanel {
    position: absolute !important;
    right: 6px !important;
    top: 50% !important;
    left: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: translateY(-50%) scale(0.54) !important;
    transform-origin: center right !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 4px !important;
    background: rgba(15, 10, 25, 0.92) !important;
    border: 1px solid rgba(255, 215, 106, 0.5) !important;
    border-radius: 12px !important;
    padding: 6px !important;
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.85) !important;
    margin: 0 !important;
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

  /* 6. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方中軸 */
  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    transform: scale(0.52) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }

  /* 7. 底部我方手牌專區 (.hand-panel) 強制底部置底，高度 95px */
  .hand-panel {
    position: fixed !important;
    bottom: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 95px !important;
    min-height: 95px !important;
    max-height: 95px !important;
    flex: 0 0 95px !important;
    z-index: 10010 !important;
    padding: 2px 8px !important;
    background: rgba(12, 8, 24, 0.96) !important;
    border-top: 1px solid rgba(255, 215, 106, 0.3) !important;
    display: flex !important;
    align-items: center !important;
    overflow: hidden !important;
    box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.8) !important;
  }

  .hand-title {
    width: 32px !important;
    flex: 0 0 32px !important;
    font-size: 10px !important;
    line-height: 1.15 !important;
    margin: 0 !important;
    padding: 0 !important;
  }

  .hand {
    flex: 1 !important;
    height: 90px !important;
    padding: 0 !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 2px !important;
  }

  .hand .card {
    width: 62px !important;
    height: 86px !important;
    min-width: 50px !important;
    flex: 0 0 62px !important;
    margin-left: -10px !important;
    transition: transform 0.2s ease, z-index 0.2s ease !important;
  }

  .hand .card:first-child {
    margin-left: 0 !important;
  }

  .hand .card:hover,
  .hand .card:active {
    z-index: 200 !important;
    transform: translateY(-12px) scale(1.22) !important;
  }

  /* 左側卡牌放大預覽面板獨立彈出適配 */
  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: absolute !important;
    left: 8px !important;
    bottom: 105px !important; /* 浮在底部手牌面板上方 */
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }
}

"""

    css_content += golden_grid_css
    
    # Also clean and update body.xlw-iphone14-sim-active to use absolute translate scale in sync
    css_content = css_content.replace(
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  width: 1400px !important;\n  height: 760px !important;\n  min-width: 1400px !important;\n  min-height: 760px !important;\n  position: absolute !important;\n  top: 52% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.40) !important;\n  transform-origin: center center !important;\n}",
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  width: 1400px !important;\n  height: 760px !important;\n  min-width: 1400px !important;\n  min-height: 760px !important;\n  position: absolute !important;\n  top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.36) !important;\n  transform-origin: center center !important;\n}"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated static/style_v8.css with mobile golden grid CSS successfully!")

    # Update cache-buster in static/index.html to v=15.80-mobile-golden-grid-layout
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.80-mobile-golden-grid-layout', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.80-mobile-golden-grid-layout', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_golden_grid()
