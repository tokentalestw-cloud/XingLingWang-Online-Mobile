# -*- coding: utf-8 -*-
import sys, re

def fix_all_in_one():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Clean old Master Duel or Welcome Splash CSS blocks to prevent conflicts
    block_marker_rwd = "/* ==========================================================================\n   REAL MOBILE DEVICE LANDSCAPE RWD"
    if block_marker_rwd in css_content:
        css_content = css_content[:css_content.find(block_marker_rwd)]

    block_marker_splash = "/* ==========================================================================\n   BATTLE CATS STYLE WELCOME SPLASH"
    if block_marker_splash in css_content:
        css_content = css_content[:css_content.find(block_marker_splash)]

    combined_css = """/* ==========================================================================
   REAL MOBILE DEVICE LANDSCAPE RWD (按鈕縮至 1/3 以下、狀態欄極致微縮靠邊、手牌防縮小固定)
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

  /* 3. 雙方分數看板 (#scoreBadgeFixed) 極度微縮、窄寬度、小字體，縮放為 32% */
  #scoreBadgeFixed {
    position: absolute !important;
    left: 6px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    background: rgba(10, 8, 20, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 6px !important;
    padding: 3px 5px !important;
    transform: scale(0.32) !important;
    transform-origin: top left !important;
    width: 155px !important; /* 長寬大幅縮短，限縮為 155px */
    height: auto !important;
    margin: 0 !important;
  }
  
  .score-badge-section {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
  }

  .score-badge-card {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  .score-badge-label {
    font-size: 9.5px !important; /* 字體縮小 */
    color: #ffd76a !important;
  }

  .score-badge-num {
    font-size: 12px !important; /* 字體縮小 */
    font-weight: bold !important;
    color: #ffffff !important;
  }

  .score-badge-subrow {
    font-size: 8px !important; /* 字體縮小 */
    opacity: 0.85 !important;
  }

  /* 4. 對手狀態欄 (#xlwEnemyInfoPanel) 極度微縮、窄寬度、小字體，縮放為 32% */
  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 6px !important;
    top: 86px !important; /* 向上靠緊分數看板 */
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.32) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 6px !important;
    padding: 3px 5px !important;
    width: 155px !important; /* 長寬大幅縮短，限縮為 155px */
    height: auto !important;
    margin: 0 !important;
    display: block !important;
  }

  #xlwEnemyInfoPanel .enemy-info-title {
    font-size: 9.5px !important; /* 字體縮小 */
    margin: 0 !important;
    white-space: nowrap !important;
  }
  
  #xlwEnemyInfoPanel .enemy-stats-row {
    margin-top: 2px !important;
    gap: 4px !important;
  }

  #xlwEnemyInfoPanel .enemy-stat-badge {
    padding: 1px 3px !important;
    font-size: 8px !important; /* 字體縮小 */
    white-space: nowrap !important;
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

  /* 7. 我方手牌專區 (.hand-panel) 釘死於視窗底部，設定固定寬度以防 Safari 折疊 Bug */
  .hand-panel {
    position: fixed !important;
    bottom: 14px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 520px !important; /* 固定寬度，防範 iOS Safari 寬度崩塌 */
    max-width: 90vw !important;
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


/* ==========================================================================
   BATTLE CATS STYLE WELCOME SPLASH SCREEN (貓咪大戰爭風格登入歡迎畫面樣式系統)
   ========================================================================== */

.xlw-welcome-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: radial-gradient(circle at 50% 50%, #170d2a 0%, #070509 100%) !important;
  z-index: 150000 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: hidden !important;
  font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important;
}

/* 漸層發光背景動畫 */
.welcome-background-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 120vw;
  height: 120vh;
  transform: translate(-50%, -50%);
  background: radial-gradient(circle, rgba(212, 175, 55, 0.15) 0%, rgba(0,0,0,0) 70%);
  animation: welcomeGlowPulse 6s infinite alternate ease-in-out;
  pointer-events: none;
}

@keyframes welcomeGlowPulse {
  0% { opacity: 0.5; transform: translate(-50%, -50%) scale(0.95); }
  100% { opacity: 1.0; transform: translate(-50%, -50%) scale(1.05); }
}

/* 背景星光粒片漂浮效果 */
.welcome-sparkles {
  position: absolute;
  width: 100%;
  height: 100%;
  background-image: 
    radial-gradient(circle, #ffd76a 1px, transparent 1px),
    radial-gradient(circle, #ffffff 1px, transparent 1px);
  background-size: 80px 80px, 120px 120px;
  background-position: 0 0, 40px 60px;
  opacity: 0.35;
  animation: welcomeSparkleFloat 12s infinite linear;
  pointer-events: none;
}

@keyframes welcomeSparkleFloat {
  0% { transform: translateY(0); }
  100% { transform: translateY(-80px); }
}

/* 左右裝飾漂浮星靈卡牌 */
.floating-deco-card {
  position: absolute;
  width: 80px;
  height: 110px;
  border-radius: 6px;
  border: 1px solid rgba(255, 215, 106, 0.4);
  background: rgba(20, 15, 35, 0.95);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8);
  opacity: 0.65;
  pointer-events: none;
}
.floating-deco-card.card-left {
  left: 8%;
  top: 30%;
  transform: rotate(-15deg);
  background-image: radial-gradient(circle, rgba(212,175,55,0.2) 0%, transparent 80%);
  animation: floatCardL 4s infinite alternate ease-in-out;
}
.floating-deco-card.card-right {
  right: 8%;
  bottom: 25%;
  transform: rotate(18deg);
  background-image: radial-gradient(circle, rgba(255,77,79,0.2) 0%, transparent 80%);
  animation: floatCardR 4.5s infinite alternate ease-in-out;
}

@keyframes floatCardL {
  0% { transform: translateY(0) rotate(-15deg); }
  100% { transform: translateY(-16px) rotate(-10deg); }
}
@keyframes floatCardR {
  0% { transform: translateY(0) rotate(18deg); }
  100% { transform: translateY(-18px) rotate(22deg); }
}

/* 首頁容器 */
.welcome-container {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  text-align: center;
}

/* 經典霓虹字型標題 */
.welcome-title-box {
  animation: titlePulse 2s infinite alternate ease-in-out;
}
.welcome-title-eng {
  font-family: "Cinzel", "Georgia", serif !important;
  font-size: 26px !important;
  font-weight: 900 !important;
  color: #ffffff !important;
  letter-spacing: 4px !important;
  margin: 0 !important;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3) !important;
}
.welcome-title-chn {
  font-size: 42px !important;
  font-weight: 900 !important;
  color: #ffd76a !important;
  letter-spacing: 12px !important;
  margin: 6px 0 0 0 !important;
  text-shadow: 
    0 0 15px rgba(255, 215, 106, 0.8),
    0 0 30px rgba(255, 215, 106, 0.4) !important;
}

@keyframes titlePulse {
  0% { transform: scale(0.98); }
  100% { transform: scale(1.02); }
}

/* 貓咪大戰爭風格：Bouncing 吉祥物容器 */
.mascot-container {
  display: flex;
  gap: 32px;
  height: 60px;
  align-items: flex-end;
  margin: 10px 0;
}

/* 萌萌卡哇伊 Bouncing 動畫 */
.bouncing-mascot {
  width: 50px;
  height: 50px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: bottom center;
}
/* 貓貓吉祥物 */
.mascot-cat {
  background-image: url('/static/icon-192.png');
  border-radius: 50%;
  border: 1.5px solid #ffd76a;
  animation: mascotBounce 0.8s infinite alternate cubic-bezier(0.28, 0.84, 0.42, 1);
}
.mascot-beast {
  background-image: url('/static/little_traveler.jpeg');
  border-radius: 50%;
  border: 1.5px solid #ff4d4f;
  animation: mascotBounce 0.95s infinite alternate cubic-bezier(0.28, 0.84, 0.42, 1) 0.1s;
}

@keyframes mascotBounce {
  0% { transform: translateY(0) scaleY(0.92); }
  100% { transform: translateY(-24px) scaleY(1.05); }
}

/* 歡迎選單與圓角按鈕 */
.welcome-menu {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 250px;
}

.menu-btn {
  position: relative;
  width: 100%;
  padding: 14px 24px !important;
  font-size: 22px !important; /* 大幅放大字體 */
  font-weight: 900 !important;
  border-radius: 50px !important;
  cursor: pointer !important;
  border: 3px solid #ffd76a !important; /* 加粗邊框 */
  color: #ffe600 !important; /* 明亮金黃 */
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 12px !important;
  overflow: hidden !important;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.95), 0 0 10px rgba(0, 0, 0, 0.9) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.8) !important;
}

.menu-ai {
  background: linear-gradient(135deg, #1b0d2b 0%, #3e1b6f 100%) !important;
  box-shadow: 0 4px 15px rgba(82, 196, 26, 0.15);
}
.menu-multi {
  background: linear-gradient(135deg, #2b0d18 0%, #6f1b3c 100%) !important;
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.3) !important;
  border-color: #ff4d4f !important;
  color: #ff6b6b !important;
}
.menu-builder {
  background: linear-gradient(135deg, #221c0d 0%, #523f10 100%) !important;
  box-shadow: 0 4px 15px rgba(212, 175, 55, 0.15);
}

.menu-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 215, 106, 0.4);
}
.menu-btn:active {
  transform: scale(0.98);
}

.btn-shine {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.25) 50%, rgba(255,255,255,0) 100%);
  transform: skewX(-25deg);
  animation: buttonShineAnim 3s infinite linear;
}

.welcome-footer {
  font-size: 9.5px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 10px;
  letter-spacing: 0.5px;
}

.xlw-welcome-fadeout {
  animation: welcomeFadeoutAnim 0.45s forwards ease-in-out;
  pointer-events: none;
}

@media (max-width: 1024px) and (orientation: landscape) {
  .welcome-container {
    transform: scale(0.92) !important;
    transform-origin: center center !important;
    gap: 10px !important;
  }
  .menu-btn {
    padding: 10px 18px !important;
    font-size: 18px !important;
  }
}
"""

    css_content += combined_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Combined and appended style updates to style_v8.css successfully!")

    # 2. Update static/game_v8.js to use robust immediate showWelcomeOverlayOnLoad logic
    js_content = open(js_path, encoding='utf-8').read()

    # Locate and update the bottom event listener in js
    old_listener = """// 確保點開頁面時自動調用首頁顯示
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.style.display = "flex";
  }
});"""

    new_listener = """// 確保點開頁面時自動調用首頁顯示 (抗 Safari 競態條件載入引擎)
function showWelcomeOverlayOnLoad() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.style.display = "flex";
    console.log("Welcome overlay displayed on load!");
  }
}
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", showWelcomeOverlayOnLoad);
} else {
  showWelcomeOverlayOnLoad();
}"""

    if old_listener in js_content:
        js_content = js_content.replace(old_listener, new_listener)
    else:
        # Fallback replacement
        js_content = re.sub(
            r'document\.addEventListener\("DOMContentLoaded",\s*\(\)\s*=>\s*\{\s*const\s*overlay\s*=\s*document\.getElementById\("xlwWelcomeOverlay"\);.*?\n\}\);',
            new_listener,
            js_content,
            flags=re.DOTALL
        )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Injected robust welcome loading triggers in game_v8.js successfully!")

    # Update cache-buster in static/index.html to v=17.50-fixed-welcome-and-shrunk-side-panels
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.50-fixed-welcome-and-shrunk-side-panels', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.50-fixed-welcome-and-shrunk-side-panels', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_all_in_one()
