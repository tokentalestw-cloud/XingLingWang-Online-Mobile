# -*- coding: utf-8 -*-
import sys, re

def fix_clean_inside_dom():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/game_v8.js to cleanly move elements in/out of .game-shell during sim mode
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    clean_dom_sim_js = """
// ===== 📱 iPhone 14 橫向擬真螢幕模擬器 (DOM 容器內部完整包含，排版0混亂) =====
window.xlwIphone14SimActive = localStorage.getItem('xlw_iphone14_sim') === 'true';

window.xlwToggleIphone14Sim = function() {
  window.xlwIphone14SimActive = !window.xlwIphone14SimActive;
  localStorage.setItem('xlw_iphone14_sim', window.xlwIphone14SimActive ? 'true' : 'false');
  window.xlwApplyIphone14SimState();
};

window.xlwApplyIphone14SimState = function() {
  const btn = document.getElementById("xlwIphone14SimBtn");
  const gameShell = document.querySelector(".game-shell");
  const topbar = document.querySelector(".topbar-grouped-v9");
  const phasePanel = document.getElementById("phaseDisplayPanelHard");
  const enemyPanel = document.getElementById("xlwEnemyInfoPanel");
  const stablePanel = document.getElementById("stableActionPanel");

  if (!gameShell) return;

  if (window.xlwIphone14SimActive) {
    document.body.classList.add("xlw-iphone14-sim-active");
    if (btn) btn.innerHTML = "📱 關閉 iPhone 模擬";

    // 移入 .game-shell 內部
    if (topbar && topbar.parentElement !== gameShell) gameShell.insertBefore(topbar, gameShell.firstChild);
    if (phasePanel && phasePanel.parentElement !== gameShell) gameShell.appendChild(phasePanel);
    if (enemyPanel && enemyPanel.parentElement !== gameShell) gameShell.appendChild(enemyPanel);
    if (stablePanel && stablePanel.parentElement !== gameShell) gameShell.appendChild(stablePanel);
  } else {
    document.body.classList.remove("xlw-iphone14-sim-active");
    if (btn) btn.innerHTML = "📱 iPhone 14 模擬";

    // 還原移回 document.body 外部
    if (topbar && topbar.parentElement === gameShell) document.body.insertBefore(topbar, gameShell);
    if (phasePanel && phasePanel.parentElement === gameShell) document.body.insertBefore(phasePanel, gameShell);
    if (enemyPanel && enemyPanel.parentElement === gameShell) document.body.appendChild(enemyPanel);
    if (stablePanel && stablePanel.parentElement === gameShell) document.body.appendChild(stablePanel);
  }
};

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(() => {
    if (typeof window.xlwApplyIphone14SimState === 'function') window.xlwApplyIphone14SimState();
  }, 150);
});
"""

    if "window.xlwToggleIphone14Sim" in js_content:
        block_start = js_content.find("// ===== 📱 iPhone 14 橫向擬真螢幕模擬器")
        if block_start >= 0:
            js_content = js_content[:block_start] + clean_dom_sim_js
        else:
            js_content += "\n" + clean_dom_sim_js

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated static/game_v8.js with clean DOM element reparenting logic successfully!")

    # 2. Update static/style_v8.css with clean absolute positioning relative to .game-shell
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS block
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    clean_inner_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (.game-shell 內部純淨定位，排版 100% 完美不混亂)
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

/* iPhone 14 實體機身外殼 (844px x 390px) */
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
  display: block !important;
  background: #070505 !important;
}

/* 1. 工具列 (Top Bar) 融入 iPhone 14 視窗最上方 */
body.xlw-iphone14-sim-active .game-shell .topbar-grouped-v9 {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 38px !important;
  min-height: 38px !important;
  padding: 0 12px !important;
  margin: 0 !important;
  transform: none !important;
  z-index: 10020 !important;
  background: rgba(12, 8, 20, 0.96) !important;
  border-bottom: 1px solid rgba(212, 175, 55, 0.5) !important;
  border-radius: 0 !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.8) !important;
}

body.xlw-iphone14-sim-active .game-shell .topbar-brand {
  font-size: 14px !important;
}

body.xlw-iphone14-sim-active .game-shell .topbar-group {
  padding: 2px 6px !important;
  gap: 4px !important;
}

body.xlw-iphone14-sim-active .game-shell .group-label {
  font-size: 11px !important;
}

body.xlw-iphone14-sim-active .game-shell .topbar-group select {
  font-size: 11px !important;
  padding: 2px 4px !important;
}

body.xlw-iphone14-sim-active .game-shell .topbar-action-btn,
body.xlw-iphone14-sim-active .game-shell .topbar-setting-btn,
body.xlw-iphone14-sim-active .game-shell .topbar-setting-select {
  font-size: 11px !important;
  padding: 3px 8px !important;
}

/* 2. 對戰棋盤視角 (40% 縮放完全置中於 iPhone 14 內部) */
body.xlw-iphone14-sim-active .game-shell .board-wrap {
  width: 100% !important;
  height: 352px !important;
  margin-top: 38px !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  position: relative !important;
}

body.xlw-iphone14-sim-active .game-shell #boardWrap {
  zoom: 0.40 !important;
  margin: auto !important;
  transform-origin: center center !important;
}

@supports not (zoom: 0.40) {
  body.xlw-iphone14-sim-active .game-shell #boardWrap {
    transform: scale(0.40) !important;
    transform-origin: center center !important;
  }
}

/* 3. 右下角對戰操作按鈕面板 (#stableActionPanel) 獨立定位於 iPhone 14 內部右下角 */
body.xlw-iphone14-sim-active .game-shell #stableActionPanel {
  position: absolute !important;
  right: 12px !important;
  bottom: 12px !important;
  top: auto !important;
  left: auto !important;
  z-index: 10000 !important;
  transform: scale(0.72) !important;
  transform-origin: bottom right !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
  background: rgba(15, 10, 25, 0.92) !important;
  border: 1px solid rgba(255, 215, 106, 0.5) !important;
  border-radius: 12px !important;
  padding: 8px !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.85) !important;
}

body.xlw-iphone14-sim-active .game-shell #stableActionPanel .stable-action-row {
  display: flex !important;
  flex-direction: column !important;
  gap: 5px !important;
}

body.xlw-iphone14-sim-active .game-shell #stableActionPanel .stable-action-btn {
  width: 125px !important;
  font-size: 13.5px !important;
  padding: 7px 10px !important;
  white-space: nowrap !important;
}

/* 4. 中上方階段提示面板 (#phaseDisplayPanelHard) 定位於工具列下方 */
body.xlw-iphone14-sim-active .game-shell #phaseDisplayPanelHard {
  position: absolute !important;
  top: 42px !important;
  left: 50% !important;
  transform: translateX(-50%) scale(0.65) !important;
  transform-origin: top center !important;
  z-index: 10000 !important;
  display: flex !important;
}

/* 5. 左上方對手狀態欄 (#xlwEnemyInfoPanel) 定位於工具列下方左側 */
body.xlw-iphone14-sim-active .game-shell #xlwEnemyInfoPanel {
  position: absolute !important;
  top: 42px !important;
  left: 12px !important;
  transform: scale(0.65) !important;
  transform-origin: top left !important;
  z-index: 10000 !important;
  display: block !important;
}

/* 6. 左側卡牌放大預覽面板獨立彈出適配 */
body.xlw-iphone14-sim-active .game-shell .xlw-left-card-panel,
body.xlw-iphone14-sim-active .game-shell #xlwLeftCardPanel {
  position: absolute !important;
  left: 10px !important;
  bottom: 10px !important;
  top: auto !important;
  z-index: 10050 !important;
  transform: scale(0.72) !important;
  transform-origin: bottom left !important;
}

"""

    css_content += clean_inner_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated static/style_v8.css with clean inner-shell positioning successfully!")

    # Update cache-buster in static/index.html to v=14.60-iphone14-clean-inner-dom
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.60-iphone14-clean-inner-dom', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.60-iphone14-clean-inner-dom', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_clean_inside_dom()
