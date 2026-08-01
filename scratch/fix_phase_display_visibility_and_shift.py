# -*- coding: utf-8 -*-
import sys, re

def fix_phase_visibility_and_shift():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html: hide phaseDisplayPanelHard by default
    idx_content = open(idx_path, encoding='utf-8').read()

    idx_content = idx_content.replace(
        '<div id="phaseDisplayPanelHard" class="phase-display-panel-hard">',
        '<div id="phaseDisplayPanelHard" class="phase-display-panel-hard" style="display: none !important;">'
    )

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.50-phase-panel-cointoss-and-shift-left-40', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.50-phase-panel-cointoss-and-shift-left-40', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated index.html to hide phaseDisplayPanelHard by default and updated cache-busters!")

    # 2. Update static/style_v8.css: left: 245px (285px - 40px)
    css_content = open(css_path, encoding='utf-8').read()

    old_phase_style = """  #phaseDisplayPanelHard {
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
  }"""

    new_phase_style = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 2px !important;
    left: 245px !important;
    width: 960px !important;
    transform: scale(0.70) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
  }"""

    css_content = css_content.replace(old_phase_style, new_phase_style)
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated style_v8.css left to 245px for phaseDisplayPanelHard successfully!")

    # 3. Update static/game_v8.js: Show phase panel in startSinglePlayerGameActual, hide in init/title
    js_content = open(js_path, encoding='utf-8').read()

    # In startSinglePlayerGameActual, show phaseDisplayPanelHard
    start_actual_target = "function startSinglePlayerGameActual(playerGoesFirst) {"
    show_phase_code = """function startSinglePlayerGameActual(playerGoesFirst) {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "flex", "important");"""

    js_content = js_content.replace(start_actual_target, show_phase_code)

    # In xlwReturnToTitle, hide phaseDisplayPanelHard
    return_title_target = "window.xlwReturnToTitle = function() {"
    hide_phase_code = """window.xlwReturnToTitle = function() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");"""

    js_content = js_content.replace(return_title_target, hide_phase_code)

    # In initGameEmptyState, hide phaseDisplayPanelHard
    init_empty_target = "function initGameEmptyState() {"
    hide_phase_code_init = """function initGameEmptyState() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");"""

    js_content = js_content.replace(init_empty_target, hide_phase_code_init)

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("3. Updated game_v8.js startSinglePlayerGameActual/xlwReturnToTitle/initGameEmptyState to toggle phase panel visibility after coin toss!")

if __name__ == '__main__':
    fix_phase_visibility_and_shift()
