# -*- coding: utf-8 -*-
import os, sys, re

def apply_lobby_and_text_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/index.html: Shorten button text and update cache-busters
    idx = open(idx_path, encoding='utf-8').read()

    idx = idx.replace('📜 戰局紀錄', '📜 紀錄')
    idx = idx.replace('🏠 返回首頁', '🏠 首頁')

    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.70-lobby-opaque-and-buttons-shortened', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.70-lobby-opaque-and-buttons-shortened', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("1. Updated button texts and cache-busters in index.html successfully!")

    # 2. Update static/game_v8.js: Ensure opponent AI select is hidden in multi mode
    js = open(js_path, encoding='utf-8').read()

    old_mode_toggle = """  // Toggle enemy selection group
  const enemyGroup = document.getElementById("prebattleEnemyGroup");
  if (enemyGroup) {
    enemyGroup.style.display = (mode === 'single') ? "block" : "none";
  }"""

    new_mode_toggle = """  // Toggle enemy selection group (Hidden for online multi-player)
  const enemyGroup = document.getElementById("prebattleEnemyGroup");
  if (enemyGroup) {
    if (mode === 'single') {
      enemyGroup.style.setProperty("display", "block", "important");
    } else {
      enemyGroup.style.setProperty("display", "none", "important");
    }
  }"""

    js = js.replace(old_mode_toggle, new_mode_toggle)
    open(js_path, 'w', encoding='utf-8').write(js)
    print("2. Updated game_v8.js opponent deck toggle successfully!")

    # 3. Update static/style_v8.css: shrink phase text & set opaque multiplayer lobby overlay
    css = open(css_path, encoding='utf-8').read()

    # Shrink phase panel fonts
    old_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 225px !important;
    width: 960px !important;
    transform: scale(0.62) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
  }
  .phase-hard-title { font-size: 19px !important; font-weight: 900 !important; color: #ffd76a !important; text-shadow: 0 0 10px rgba(255, 215, 106, 0.5) !important; line-height: 1.1 !important; }
  .phase-hard-help { font-size: 12px !important; color: #ffe6a0 !important; line-height: 1.1 !important; margin-top: 1px !important; }"""

    new_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 225px !important;
    width: 960px !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
  }
  .phase-hard-title { font-size: 14px !important; font-weight: bold !important; color: #ffd76a !important; line-height: 1.1 !important; }
  .phase-hard-help { font-size: 10px !important; color: #ffe6a0 !important; line-height: 1.1 !important; margin-top: 1px !important; }"""

    css = css.replace(old_phase_css, new_phase_css)

    # Fullscreen opaque multiplayer lobby CSS
    multiplayer_lobby_opaque_css = """
/* 全螢幕不透明深色線上對戰大廳浮層 (#multiplayerLobby) */
#multiplayerLobby {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(8, 6, 16, 0.98) !important;
  z-index: 9999999 !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}
"""
    css += multiplayer_lobby_opaque_css

    open(css_path, 'w', encoding='utf-8').write(css)
    print("3. Updated style_v8.css phase text shrink & opaque multiplayer lobby overlay successfully!")

if __name__ == '__main__':
    apply_lobby_and_text_fixes()
