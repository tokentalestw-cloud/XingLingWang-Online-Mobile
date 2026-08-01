# -*- coding: utf-8 -*-
import sys, re

def final_realign():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html topbar buttons structure
    idx_content = open(idx_path, encoding='utf-8').read()

    old_topbar_structure = """    <!-- 2. 系統設定與戰況區塊 -->
    <div class="topbar-group settings-group">
      <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
      <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    </div>

    <!-- 3. 返回首頁區塊 (放在最右邊) -->
    <div class="topbar-group action-group">
      <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 13px !important; padding: 6px 12px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important;">🏠 返回首頁</button>
    </div>"""

    new_topbar_structure = """    <!-- 2. 系統設定與功能按鈕集中移至畫面最右邊 (返回首頁在最右側) -->
    <div class="topbar-group action-group" style="margin-left: auto !important; display: flex !important; align-items: center !important; gap: 8px !important;">
      <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
      <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
      <button id="xlwDebugToggleBtn" class="topbar-setting-btn" type="button">Debug：關</button>
      <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 13px !important; padding: 4px 12px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important; white-space: nowrap !important;">🏠 返回首頁</button>
    </div>"""

    idx_content = idx_content.replace(old_topbar_structure, new_topbar_structure)

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.20-hud-and-topbar-final-realigned', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.20-hud-and-topbar-final-realigned', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated index.html topbar buttons layout successfully!")

    # 2. Update static/game_v8.js: setupDebugToggle to use existing DOM element & renderEnemyPanel
    js_content = open(js_path, encoding='utf-8').read()

    old_debug_setup = """function setupDebugToggle() {
  const topbar = document.querySelector(".topbar");
  if (!topbar || document.getElementById("xlwDebugToggleBtn")) return;
  const btn = document.createElement("button");
  btn.id = "xlwDebugToggleBtn";
  btn.type = "button";

  const refresh = () => {
    const on = localStorage.getItem("XLW_DEBUG_ALWAYS_ON") === "1";
    btn.textContent = on ? "Debug：開" : "Debug：關";
    if (!on) {
      const panel = document.getElementById("xlwDebugPanel");
      if (panel) panel.remove();
    } else {
      createDebugPanel();
    }
  };

  btn.onclick = () => {
    const on = localStorage.getItem("XLW_DEBUG_ALWAYS_ON") === "1";
    localStorage.setItem("XLW_DEBUG_ALWAYS_ON", on ? "0" : "1");
    refresh();
  };

  topbar.appendChild(btn);
  refresh();
}"""

    new_debug_setup = """function setupDebugToggle() {
  let btn = document.getElementById("xlwDebugToggleBtn");
  if (!btn) {
    const topbar = document.querySelector(".topbar");
    if (!topbar) return;
    btn = document.createElement("button");
    btn.id = "xlwDebugToggleBtn";
    btn.type = "button";
    btn.className = "topbar-setting-btn";
    const returnBtn = document.getElementById("xlwReturnTitleBtn");
    if (returnBtn && returnBtn.parentNode) {
      returnBtn.parentNode.insertBefore(btn, returnBtn);
    } else {
      topbar.appendChild(btn);
    }
  }

  const refresh = () => {
    const on = localStorage.getItem("XLW_DEBUG_ALWAYS_ON") === "1";
    btn.textContent = on ? "Debug：開" : "Debug：關";
    if (!on) {
      const panel = document.getElementById("xlwDebugPanel");
      if (panel) panel.remove();
    } else {
      createDebugPanel();
    }
  };

  btn.onclick = () => {
    const on = localStorage.getItem("XLW_DEBUG_ALWAYS_ON") === "1";
    localStorage.setItem("XLW_DEBUG_ALWAYS_ON", on ? "0" : "1");
    refresh();
  };

  refresh();
}"""

    js_content = js_content.replace(old_debug_setup, new_debug_setup)

    old_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 10px !important; white-space: nowrap; font-weight: bold; color: #ffd76a; line-height: 1;">對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 1px 4px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.2) !important; border-radius: 3px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    new_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 10px !important; white-space: nowrap; font-weight: bold; color: #ffd76a; line-height: 1;">對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 1px 4px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.2) !important; border-radius: 3px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated game_v8.js debug button setup and renderEnemyPanel successfully!")

    # 3. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Reposition #xlwEnemyInfoPanel to left: 180px, top: 32px, width: 55px
    old_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 8px !important;
    top: 85px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 1px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 2px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
  }"""

    new_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 180px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 2px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Reposition & enlarge #phaseDisplayPanelHard (top: 2px, left: 320px, scale 0.60, title 17px, help 13px)
    old_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 32px !important;
    left: 270px !important;
    width: 960px !important;
    transform: scale(0.48) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 2px !important;
    left: 320px !important;
    width: 960px !important;
    transform: scale(0.60) !important;
    transform-origin: top left !important;
    z-index: 10000 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }
  .phase-hard-title { font-size: 17px !important; font-weight: 900 !important; color: #ffd76a !important; }
  .phase-hard-help { font-size: 13px !important; line-height: 1.3 !important; }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Repositioned #xlwEnemyInfoPanel to right of score badge and enlarged #phaseDisplayPanelHard at top: 2px, left: 320px in style_v8.css successfully!")

if __name__ == '__main__':
    final_realign()
