# -*- coding: utf-8 -*-
import sys, re, os

def implement_welcome_splash():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    if not os.path.exists(idx_path):
        print(f"Error: {idx_path} not found. Please run this script in the root of the project.")
        sys.exit(1)

    # 1. Update static/index.html to add Welcome Splash Screen and Back to Title button
    idx_content = open(idx_path, encoding='utf-8').read()

    # Hide the old mode-group in HTML by changing class or removing it
    idx_content = idx_content.replace(
        '<div class="topbar-group mode-group">',
        '<div class="topbar-group mode-group" style="display: none !important;">'
    )

    # Add Return to Title button to settings-group
    settings_btn_html = '<button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #1c152a 0%, #2c2244 100%) !important; border: 1px solid #ffd76a !important; color: #ffd76a !important; font-weight: bold !important;">🏠 返回主選單</button>'
    if 'xlwReturnTitleBtn' not in idx_content:
        idx_content = idx_content.replace(
            '<button id="xlwHistoryBtn"',
            f'{settings_btn_html}\n    <button id="xlwHistoryBtn"'
        )

    # Add Welcome Overlay HTML
    welcome_overlay_html = """  <!-- 🐱 貓咪大戰爭風格之星靈王登入歡迎首頁 (Battle Cats Style Welcome Splash Screen) -->
  <div id="xlwWelcomeOverlay" class="xlw-welcome-overlay">
    <div class="welcome-background-glow"></div>
    <div class="welcome-sparkles"></div>
    
    <!-- 漂浮裝飾星靈卡牌 -->
    <div class="floating-deco-card card-left"></div>
    <div class="floating-deco-card card-right"></div>

    <div class="welcome-container">
      <!-- 經典發光大標題 -->
      <div class="welcome-title-box">
        <h1 class="welcome-title-eng">XINGLINGWANG</h1>
        <h2 class="welcome-title-chn">星 靈 王</h2>
      </div>

      <!-- 貓咪大戰爭風格：萌動 Bouncing 星靈貓貓吉祥物 -->
      <div class="mascot-container">
        <div class="bouncing-mascot mascot-cat"></div>
        <div class="bouncing-mascot mascot-beast"></div>
      </div>

      <!-- 三大遊戲模式主入口按鈕 -->
      <div class="welcome-menu">
        <button class="menu-btn menu-ai" onclick="window.xlwChooseMode('single')">
          <span class="btn-icon">⚔️</span>
          <span class="btn-text">單人對抗 AI</span>
          <span class="btn-shine"></span>
        </button>
        
        <button class="menu-btn menu-multi" onclick="window.xlwChooseMode('multi')">
          <span class="btn-icon">🌐</span>
          <span class="btn-text">線上雙人對決</span>
          <span class="btn-shine"></span>
        </button>
        
        <a href="/static/deck_builder.html" style="text-decoration: none; width: 100%; display: flex; justify-content: center;">
          <button class="menu-btn menu-builder" type="button">
            <span class="btn-icon">🎴</span>
            <span class="btn-text">牌組編輯器</span>
            <span class="btn-shine"></span>
          </button>
        </a>
      </div>
      
      <!-- 底部版權聲明 -->
      <div class="welcome-footer">
        © 2026 XINGLINGWANG Studio. All Rights Reserved.
      </div>
    </div>
  </div>"""

    if 'xlwWelcomeOverlay' not in idx_content:
        idx_content = idx_content.replace('</body>', f'{welcome_overlay_html}\n</body>')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Added Welcome Splash Screen HTML and Back-to-Title button to index.html successfully!")

    # 2. Update static/style_v8.css with Battle Cats style Welcome Splash CSS and animations
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old Master Duel css priority blocks to avoid duplicates
    block_marker = "/* ==========================================================================\n   BATTLE CATS STYLE WELCOME SPLASH"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    welcome_css = """/* ==========================================================================
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
/* 貓貓吉祥物 (利用內建貓貓頭圖示或繪製) */
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
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 900;
  border-radius: 50px;
  cursor: pointer;
  border: 2px solid #ffd76a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
}

.menu-ai {
  background: linear-gradient(135deg, #1b0d2b 0%, #3e1b6f 100%) !important;
  box-shadow: 0 4px 15px rgba(82, 196, 26, 0.15);
}
.menu-multi {
  background: linear-gradient(135deg, #2b0d18 0%, #6f1b3c 100%) !important;
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.15);
  border-color: #ff4d4f !important;
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

/* 按鈕流光閃爍特效 */
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
@keyframes buttonShineAnim {
  0% { left: -100%; }
  40% { left: 150%; }
  100% { left: 150%; }
}

.welcome-footer {
  font-size: 9.5px;
  color: rgba(255, 255, 255, 0.3);
  margin-top: 10px;
  letter-spacing: 0.5px;
}

/* 轉場動畫淡出效果 */
.xlw-welcome-fadeout {
  animation: welcomeFadeoutAnim 0.45s forwards ease-in-out;
  pointer-events: none;
}
@keyframes welcomeFadeoutAnim {
  0% { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.08); visibility: hidden; }
}

/* RWD 橫屏微調 */
@media (max-width: 1024px) and (orientation: landscape) {
  .welcome-container {
    transform: scale(0.8);
    transform-origin: center center;
    gap: 12px;
  }
}

"""

    css_content += welcome_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Added Welcome Splash Screen CSS to static/style_v8.css successfully!")

    # 3. Update static/game_v8.js to bind overlay triggers and return to title function
    js_content = open(js_path, encoding='utf-8').read()

    welcome_routing_js = """
// ===== 🏠 貓咪大戰爭風格登入首頁選單與模式控制引擎 =====
window.xlwChooseMode = function(mode) {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.display = "none";
    }, 450);
  }
  
  if (mode === 'single') {
    // 進入單人對決模式
    const select = document.getElementById("factionSelect");
    const faction = select ? select.value : "藝術品";
    const oppSelect = document.getElementById("opponentSelect");
    const oppFaction = oppSelect ? oppSelect.value : "隨機牌組";
    
    // 初始化單人對戰
    isMultiplayer = false;
    isMyTurn = true;
    
    // 觸發重新開始戰局
    const restartBtn = document.getElementById("restartBtn");
    if (restartBtn) restartBtn.click();
    console.log("Single-player AI Mode launched!");
  } else if (mode === 'multi') {
    // 進入線上雙人對決模式
    const multiPlayBtn = document.getElementById("multiPlayBtn");
    if (multiPlayBtn) {
      // 模擬點擊原本隱藏的線上雙人對決按鈕
      multiPlayBtn.click();
    }
    console.log("Online Multiplayer Mode launched!");
  }
};

window.xlwReturnToTitle = function() {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.remove("xlw-welcome-fadeout");
    overlay.style.display = "flex";
  }
  console.log("Returned to Main Welcome Splash Screen successfully!");
};

// 確保點開頁面時自動調用首頁顯示
document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.style.display = "flex";
  }
});
"""

    if "window.xlwChooseMode" not in js_content:
        js_content += "\n" + welcome_routing_js

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("3. Injected welcome routing engine into static/game_v8.js successfully!")

    # Update cache-buster in static/index.html to v=17.00-battle-cats-welcome-splash
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.00-battle-cats-welcome-splash', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.00-battle-cats-welcome-splash', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("4. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    implement_welcome_splash()
