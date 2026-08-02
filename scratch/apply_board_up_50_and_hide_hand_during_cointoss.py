# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/game_v8.js: Strict check in renderEnemyFloatingHand to hide during coin toss, welcome, & prebattle modal
    js_content = open(js_path, encoding='utf-8').read()

    old_floating_func = """function renderEnemyFloatingHand() {
  let container = document.getElementById("xlwEnemyFloatingHand");
  if (!container) {
    container = document.createElement("div");
    container.id = "xlwEnemyFloatingHand";
    container.className = "xlw-enemy-floating-hand";
    document.body.appendChild(container);
  }
  
  if (!window.XLW_gameInProgress) {
    container.style.display = "none";
    return;
  }
  
  container.style.display = "flex";"""

    new_floating_func = """function renderEnemyFloatingHand() {
  let container = document.getElementById("xlwEnemyFloatingHand");
  if (!container) {
    container = document.createElement("div");
    container.id = "xlwEnemyFloatingHand";
    container.className = "xlw-enemy-floating-hand";
    document.body.appendChild(container);
  }
  
  const coinOverlay = document.getElementById("xlwCoinOverlay");
  const coinShowing = coinOverlay && coinOverlay.style.display !== "none" && coinOverlay.style.display !== "";
  const welcomeOverlay = document.getElementById("xlwWelcomeOverlay");
  const welcomeShowing = welcomeOverlay && welcomeOverlay.style.display !== "none" && welcomeOverlay.style.display !== "";
  const prebattleModal = document.getElementById("xlwPreBattleDeckSelectOverlay");
  const prebattleShowing = prebattleModal && prebattleModal.style.display !== "none" && prebattleModal.style.display !== "";

  if (!window.XLW_gameInProgress || coinShowing || welcomeShowing || prebattleShowing) {
    container.style.setProperty("display", "none", "important");
    return;
  }
  
  container.style.setProperty("display", "flex", "important");"""

    js_content = js_content.replace(old_floating_func, new_floating_func)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated game_v8.js renderEnemyFloatingHand to hide during coin toss successfully!")

    # 2. Update static/style_v8.css: Shift board upward by 50 units (top: calc(50% + 50px) / calc(30% + 50px))
    css_content = open(css_path, encoding='utf-8').read()

    css_content = css_content.replace(
        'top: calc(50% + 100px) !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;',
        'top: calc(50% + 50px) !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;'
    )

    css_content = css_content.replace(
        'top: calc(30% + 100px) !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;',
        'top: calc(30% + 50px) !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;'
    )

    # Set default display: none on .xlw-enemy-floating-hand
    css_content = css_content.replace(
        'position: absolute !important;\n  top: -20px !important;',
        'position: absolute !important;\n  top: -20px !important;\n  display: none;'
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated style_v8.css board top positioning to +50px successfully!")

    # 3. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.70-board-up-50-and-hide-hand-during-cointoss', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.70-board-up-50-and-hide-hand-during-cointoss', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
