# -*- coding: utf-8 -*-
import os, sys, re

def fix():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update index.html
    idx = open(idx_path, encoding='utf-8').read()
    idx = idx.replace('<div id="phaseDisplayPanelHard" class="phase-display-panel-hard">', '<div id="phaseDisplayPanelHard" class="phase-display-panel-hard" style="display: none !important;">')
    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.50-phase-panel-cointoss-and-shift-left-40', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.50-phase-panel-cointoss-and-shift-left-40', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("1. Updated index.html successfully!")

    # 2. Update style_v8.css
    css = open(css_path, encoding='utf-8').read()
    old_p = 'left: 285px !important;'
    new_p = 'left: 245px !important;\n    display: none;'
    css = css.replace(old_p, new_p)
    open(css_path, 'w', encoding='utf-8').write(css)
    print("2. Updated style_v8.css successfully!")

    # 3. Update game_v8.js
    js = open(js_path, encoding='utf-8').read()
    js = js.replace('function startSinglePlayerGameActual(playerGoesFirst) {', 'function startSinglePlayerGameActual(playerGoesFirst) {\n  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");\n  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "flex", "important");')
    js = js.replace('window.xlwReturnToTitle = function() {', 'window.xlwReturnToTitle = function() {\n  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");\n  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");')
    js = js.replace('function initGameEmptyState() {', 'function initGameEmptyState() {\n  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");\n  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");')
    open(js_path, 'w', encoding='utf-8').write(js)
    print("3. Updated game_v8.js successfully!")

if __name__ == '__main__':
    fix()
