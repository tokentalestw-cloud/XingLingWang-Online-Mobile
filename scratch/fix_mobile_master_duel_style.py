# -*- coding: utf-8 -*-
import sys, re

def fix_master_duel_style():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/game_v8.js adjustBoardScale to scale the battlefield to 44% for maximum battlefield visibility
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
      // 📱 橫向手機：最大化戰場 (0.44 比例置中)
      finalScale = 0.44;
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

    # 2. Update static/style_v8.css with the Master Duel layout CSS
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old mobile RWD CSS block at the bottom
    block_marker = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    master_duel_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (遊戲王 Master Duel 懸浮立體手牌與兩側極簡化排版)
   ========================================================================== */

@media (max-width: 1024px) and (orientation: landscape) {
  html, body {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
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

  /* 1. 最上排工具列 (Top Bar) 0.42 大幅微縮，完全收納於頂部 */
  .topbar-grouped-v9 {
    position: absolute !important;
    top: 2px !important;
    left: 2px !important;
    width: 1480px !important;
    height: 28px !important;
    min-height: 28px !important;
    padding: 0 4px !important;
    margin: 0 !important;
    transform: scale(0.42) !important;
    transform-origin: top left !important;
    z-index: 10020 !important;
    background: rgba(12, 8, 20, 0.96) !important;
    border: 1px solid rgba(212, 175, 55, 0.5) !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
  }

  /* 2. 對戰棋盤放大為 scale(0.44) 絕對居中，極大化戰場視野 */
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
    transform: translate(-50%, -50%) scale(0.44) !important;
    transform-origin: center center !important;
    margin: 0 !important;
  }

  /* 3. 我方得分看板 (Master Duel 圓形浮動綠光效果) -> 靠左下角 */
  .score-badge-fixed.score-p1 {
    position: absolute !important;
    left: 12px !important;
    bottom: 12px !important;
    top: auto !important;
    right: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.88) !important;
    border: 2.5px solid #52c41a !important;
    border-radius: 50% !important;
    width: 60px !important;
    height: 60px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 0 15px rgba(82, 196, 26, 0.5) !important;
    transform: none !important;
    margin: 0 !important;
  }

  /* 4. 對手得分看板 (Master Duel 圓形浮動紅光效果) -> 靠右上角 */
  .score-badge-fixed.score-p2 {
    position: absolute !important;
    right: 12px !important;
    top: 12px !important;
    left: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.88) !important;
    border: 2.5px solid #ff4d4f !important;
    border-radius: 50% !important;
    width: 60px !important;
    height: 60px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 0 15px rgba(255, 77, 79, 0.5) !important;
    transform: none !important;
    margin: 0 !important;
  }

  /* 圓形分數牌內部文字微縮 */
  .score-badge-fixed .score-badge-label {
    font-size: 8px !important;
    color: #ffd76a !important;
    margin: 0 !important;
    line-height: 1 !important;
  }
  .score-badge-fixed .score-badge-num {
    font-size: 14px !important;
    font-weight: 900 !important;
    margin-top: 2px !important;
    line-height: 1 !important;
  }

  /* 5. 對手狀態欄 (#xlwEnemyInfoPanel) 縮小為 50% 並靠左側，分數板下方 */
  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 12px !important;
    top: 85px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    margin: 0 !important;
    display: block !important;
  }

  /* 6. 右側操作按鈕面板 (#stableActionPanel) 轉為直立懸浮 pill 柱靠右下角 */
  #stableActionPanel {
    position: absolute !important;
    right: 12px !important;
    bottom: 12px !important;
    top: auto !important;
    left: auto !important;
    z-index: 10000 !important;
    transform: scale(0.68) !important;
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
    width: 120px !important;
    font-size: 13.5px !important;
    padding: 8px 10px !important;
    border-radius: 50px !important;
    border: 2px solid #ffd76a !important;
    box-shadow: 0 0 12px rgba(255, 215, 106, 0.4) !important;
    white-space: nowrap !important;
  }

  /* 7. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方中軸 */
  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 20px !important;
    left: 450px !important;
    transform: scale(0.52) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
  }

  /* 8. 懸浮 3D 立體我方手牌區 (移除任何實體底板與文字，直接浮於戰場底部) */
  .hand-panel {
    position: absolute !important;
    bottom: 2px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: auto !important;
    height: 72px !important;
    min-height: 72px !important;
    max-height: 72px !important;
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

  /* 立體傾斜手牌 (perspective 3D rotateX) */
  .hand .card {
    width: 48px !important;
    height: 66px !important;
    min-width: 42px !important;
    flex: 0 0 48px !important;
    margin-left: -6px !important;
    border-radius: 4px !important;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.7) !important;
    transform: perspective(300px) rotateX(12deg) !important;
    transition: transform 0.25s cubic-bezier(0.25, 0.8, 0.25, 1), z-index 0.15s ease !important;
    transform-origin: bottom center !important;
  }

  .hand .card:first-child {
    margin-left: 0 !important;
  }

  /* 手牌 Hover/Touch 浮起並放大 1.4 倍，拉高顯示 */
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
    bottom: 80px !important;
    top: auto !important;
    z-index: 10050 !important;
    transform: scale(0.65) !important;
    transform-origin: bottom left !important;
  }
}

"""

    css_content += master_duel_css
    
    # Also clean and update body.xlw-iphone14-sim-active to use absolute translate scale in sync
    css_content = css_content.replace(
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  width: 1400px !important;\n  height: 760px !important;\n  min-width: 1400px !important;\n  min-height: 760px !important;\n  position: absolute !important;\n  top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.36) !important;\n  transform-origin: center center !important;\n}",
        "body.xlw-iphone14-sim-active .game-shell #boardWrap {\n  width: 1400px !important;\n  height: 760px !important;\n  min-width: 1400px !important;\n  min-height: 760px !important;\n  position: absolute !important;\n  top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;\n  transform-origin: center center !important;\n}"
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated static/style_v8.css with Master Duel layout successfully!")

    # Update cache-buster in static/index.html to v=15.90-master-duel-pwa-style
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.90-master-duel-pwa-style', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.90-master-duel-pwa-style', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_master_duel_style()
