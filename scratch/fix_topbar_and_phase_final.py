# -*- coding: utf-8 -*-
import os, sys, re

def apply_final_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/index.html
    idx = open(idx_path, encoding='utf-8').read()

    # Hide xlwFixedTopRightActionBar by default
    idx = idx.replace(
        '<div id="xlwFixedTopRightActionBar" class="xlw-fixed-top-right-action-bar">',
        '<div id="xlwFixedTopRightActionBar" class="xlw-fixed-top-right-action-bar" style="display: none !important;">'
    )

    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.60-clean-topbar-and-phase-shifted', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.60-clean-topbar-and-phase-shifted', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("1. Updated index.html successfully!")

    # 2. Update static/style_v8.css
    css = open(css_path, encoding='utf-8').read()

    # Remove topbar background/borders completely
    topbar_clean_css = """
/* 徹底移除頂層工具列邊框與底色 */
.topbar, .topbar-grouped-v9 {
  background: transparent !important;
  border: none !important;
  border-bottom: none !important;
  box-shadow: none !important;
}
"""
    css += topbar_clean_css

    # Update xlw-fixed-top-right-action-bar style: display: none, scale(0.82)
    old_top_right_css = """.xlw-fixed-top-right-action-bar {
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
}"""

    new_top_right_css = """.xlw-fixed-top-right-action-bar {
  position: fixed !important;
  top: 4px !important;
  right: 6px !important;
  left: auto !important;
  bottom: auto !important;
  z-index: 999999 !important;
  display: none;
  align-items: center !important;
  gap: 4px !important;
  background: rgba(12, 8, 22, 0.92) !important;
  border: 1px solid rgba(255, 215, 106, 0.4) !important;
  border-radius: 50px !important;
  padding: 2px 6px !important;
  transform: scale(0.82) !important;
  transform-origin: top right !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6) !important;
}
.xlw-fixed-top-right-action-bar button {
  height: 24px !important;
  font-size: 11px !important;
  padding: 1px 6px !important;
  white-space: nowrap !important;
}"""

    css = css.replace(old_top_right_css, new_top_right_css)

    # Update phaseDisplayPanelHard in CSS: left 225px (245px - 20px), top: 0px, scale 0.62
    old_phase_css = """  #phaseDisplayPanelHard {
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

    new_phase_css = """  #phaseDisplayPanelHard {
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

    css = css.replace(old_phase_css, new_phase_css)

    open(css_path, 'w', encoding='utf-8').write(css)
    print("2. Updated style_v8.css successfully!")

    # 3. Update static/game_v8.js
    js = open(js_path, encoding='utf-8').read()

    # Show xlwFixedTopRightActionBar in startSinglePlayerGameActual
    old_start = """function startSinglePlayerGameActual(playerGoesFirst) {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "flex", "important");"""

    new_start = """function startSinglePlayerGameActual(playerGoesFirst) {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "flex", "important");
  const topBarBtn = document.getElementById("xlwFixedTopRightActionBar");
  if (topBarBtn) topBarBtn.style.setProperty("display", "flex", "important");"""

    js = js.replace(old_start, new_start)

    # Hide xlwFixedTopRightActionBar in xlwReturnToTitle
    old_return = """window.xlwReturnToTitle = function() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");"""

    new_return = """window.xlwReturnToTitle = function() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");
  const topBarBtn = document.getElementById("xlwFixedTopRightActionBar");
  if (topBarBtn) topBarBtn.style.setProperty("display", "none", "important");"""

    js = js.replace(old_return, new_return)

    # Hide xlwFixedTopRightActionBar in initGameEmptyState
    old_init = """function initGameEmptyState() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");"""

    new_init = """function initGameEmptyState() {
  const hardPhasePanel = document.getElementById("phaseDisplayPanelHard");
  if (hardPhasePanel) hardPhasePanel.style.setProperty("display", "none", "important");
  const topBarBtn = document.getElementById("xlwFixedTopRightActionBar");
  if (topBarBtn) topBarBtn.style.setProperty("display", "none", "important");"""

    js = js.replace(old_init, new_init)

    open(js_path, 'w', encoding='utf-8').write(js)
    print("3. Updated game_v8.js successfully!")

if __name__ == '__main__':
    apply_final_fixes()
