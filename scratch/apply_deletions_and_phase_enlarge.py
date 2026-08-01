# -*- coding: utf-8 -*-
import sys, re

def apply_deletions_and_enlarge():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove topbar-brand (星靈王 logo)
    idx_content = re.sub(r'<div class="topbar-brand">[\s\S]*?</div>', '', idx_content)

    # Remove Debug button from top-right bar
    idx_content = idx_content.replace(
        '<button id="xlwDebugToggleBtn" class="topbar-setting-btn" type="button">Debug：關</button>',
        ''
    )

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.40-deletions-and-phase-enlarged', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.40-deletions-and-phase-enlarged', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Removed topbar-brand and Debug button in index.html successfully!")

    # 2. Update static/game_v8.js
    js_content = open(js_path, encoding='utf-8').read()

    # Disable renderEnemyPanel (hide element)
    old_render_enemy = """function renderEnemyPanel() {
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

    new_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel");
  if (panel) panel.style.display = "none";
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)

    # Safe setupDebugToggle
    old_debug_setup = """function setupDebugToggle() {
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

    new_debug_setup = """function setupDebugToggle() {
  const btn = document.getElementById("xlwDebugToggleBtn");
  if (!btn) return;
}"""

    js_content = js_content.replace(old_debug_setup, new_debug_setup)

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated game_v8.js renderEnemyPanel & setupDebugToggle successfully!")

    # 3. Update static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Hide enemy info panel, topbar brand, and debug toggle button completely
    hiding_styles = """
/* 徹底移除對手手牌狀態欄、頂部品牌 Logo 與 Debug 按鈕 */
#xlwEnemyInfoPanel, .xlw-enemy-info-panel, .topbar-brand, #xlwDebugToggleBtn {
  display: none !important;
}
"""
    css_content += hiding_styles

    # Update phaseDisplayPanelHard in mobile landscape block: left 285px (left 10px from 295px), scale 0.70, enlarged fonts
    old_phase_style = """  #phaseDisplayPanelHard {
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

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 2px !important;
    left: 285px !important;
    width: 960px !important;
    transform: scale(0.70) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
  }
  .phase-hard-title { font-size: 22px !important; font-weight: 900 !important; color: #ffd76a !important; text-shadow: 0 0 12px rgba(255, 215, 106, 0.5) !important; }
  .phase-hard-help { font-size: 15px !important; color: #ffe6a0 !important; line-height: 1.3 !important; }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Updated style_v8.css to delete enemy panel/brand/debug button and enlarge phase text shifted to left 285px successfully!")

if __name__ == '__main__':
    apply_deletions_and_enlarge()
