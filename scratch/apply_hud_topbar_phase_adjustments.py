# -*- coding: utf-8 -*-
import sys, re

def apply_adjustments():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html: Inject independent top-right action bar
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove action-group from topbar if present
    old_topbar_action_group = r'<div class="topbar-group action-group"[^>]*>[\s\S]*?</div>'
    idx_content = re.sub(old_topbar_action_group, '', idx_content)

    top_right_action_bar_html = """  <!-- 獨立置頂最右上角功能按鈕列 (返回首頁在最右側) -->
  <div id="xlwFixedTopRightActionBar" class="xlw-fixed-top-right-action-bar">
    <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
    <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    <button id="xlwDebugToggleBtn" class="topbar-setting-btn" type="button">Debug：關</button>
    <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 12px !important; padding: 4px 10px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important; white-space: nowrap !important;">🏠 返回首頁</button>
  </div>"""

    # Inject right inside <body> tag
    idx_content = idx_content.replace('<body>', '<body>\n' + top_right_action_bar_html)

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.30-hud-topbar-phase-perfected', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.30-hud-topbar-phase-perfected', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Injected xlwFixedTopRightActionBar in index.html successfully!")

    # 2. Update static/game_v8.js: setupDebugToggle and renderEnemyPanel
    js_content = open(js_path, encoding='utf-8').read()

    old_debug_setup = """function setupDebugToggle() {
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

    new_debug_setup = """function setupDebugToggle() {
  const btn = document.getElementById("xlwDebugToggleBtn");
  if (!btn) return;

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
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important; font-weight: 900; color: #ffd76a; line-height: 1.1; white-space: nowrap;">對手<br>手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 3px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important; padding: 1px 2px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.2) !important; border-radius: 3px !important; width: 100% !important; text-align: center !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated game_v8.js setupDebugToggle & renderEnemyPanel successfully!")

    # 3. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Reposition #xlwEnemyInfoPanel to left: 175px, top: 32px, width: 38px
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
    left: 175px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 2px 3px !important;
    margin: 0 !important;
    display: block !important;
    width: 38px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Reposition #phaseDisplayPanelHard to left: 295px, top: 2px, z-index: 999999
    old_phase_style = """  #phaseDisplayPanelHard {
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
  }"""

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 2px !important;
    left: 295px !important;
    width: 960px !important;
    transform: scale(0.60) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)

    # Append styles for xlw-fixed-top-right-action-bar
    top_right_bar_css = """

/* ===== 獨立置頂最右上角功能按鈕列 ===== */
.xlw-fixed-top-right-action-bar {
  position: fixed !important;
  top: 6px !important;
  right: 8px !important;
  left: auto !important;
  bottom: auto !important;
  z-index: 999999 !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: rgba(12, 8, 22, 0.92) !important;
  border: 1.5px solid rgba(255, 215, 106, 0.45) !important;
  border-radius: 50px !important;
  padding: 4px 10px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7) !important;
}

.xlw-fixed-top-right-action-bar button {
  height: 28px !important;
  font-size: 12px !important;
  padding: 2px 8px !important;
  white-space: nowrap !important;
}
"""
    css_content += top_right_bar_css

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Repositioned #xlwEnemyInfoPanel to width: 38px, left: 175px, top: 32px, phase panel to left: 295px with z-index: 999999, and added top-right action bar styles in style_v8.css successfully!")

if __name__ == '__main__':
    apply_adjustments()
