# -*- coding: utf-8 -*-
import os, sys, re

def fix_all_issues():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Fix static/index.html broken HTML string
    idx = open(idx_path, encoding='utf-8').read()

    # Locate and clean up the broken score-box HTML tag
    broken_tag_pattern = r'<div class="score-box"[^>]*>[\s\S]*?<button onclick="hideMultiplayerLobby\(\)"'
    
    clean_score_box = """<div class="score-box" style="position: relative; width: 440px; padding: 25px; border: 2px solid #ffd76a; border-radius: 12px; background: rgba(15, 11, 11, 0.95); box-shadow: 0 10px 40px rgba(0,0,0,0.95); font-family: sans-serif;">
      <div style="position: absolute; top: 12px; right: 12px; z-index: 10;">
        <button onclick="hideMultiplayerLobby(); if(window.xlwReturnToTitle) window.xlwReturnToTitle();" class="topbar-pill-btn">🏠 首頁</button>
      </div>
      <button onclick="hideMultiplayerLobby()\""""

    idx = re.sub(broken_tag_pattern, clean_score_box, idx)

    idx = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.00-html-fixed-buttons-unified-phase-shrunk', idx)
    idx = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.00-html-fixed-buttons-unified-phase-shrunk', idx)
    open(idx_path, 'w', encoding='utf-8').write(idx)
    print("1. Fixed broken HTML syntax in index.html successfully!")

    # 2. Update static/style_v8.css: Ultra-specific unified buttons CSS & shrink phase panel to 0.38
    css = open(css_path, encoding='utf-8').read()

    # Ultra-specific unified button styling for all action buttons
    unified_buttons_override = """
/* ===== 超高權重 100% 統一右上角按鈕樣式 (圓角金邊膠囊款) ===== */
#xlwFixedTopRightActionBar button,
#xlwFixedTopRightActionBar .topbar-pill-btn,
#xlwFixedTopRightActionBar #scoreBtn,
#xlwFixedTopRightActionBar #xlwSfxToggleBtn,
#xlwFixedTopRightActionBar #xlwReturnTitleBtn,
.score-box .topbar-pill-btn {
  background: linear-gradient(135deg, rgba(30, 20, 45, 0.95) 0%, rgba(15, 10, 25, 0.98) 100%) !important;
  border: 1.5px solid #ffd76a !important;
  border-radius: 50px !important;
  color: #ffd76a !important;
  font-weight: bold !important;
  font-size: 11px !important;
  padding: 3px 12px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.6), 0 0 6px rgba(255, 215, 106, 0.2) !important;
  cursor: pointer !important;
  white-space: nowrap !important;
  height: 24px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  transition: all 0.2s ease !important;
  outline: none !important;
  margin: 0 !important;
}

#xlwFixedTopRightActionBar button:hover,
#xlwFixedTopRightActionBar .topbar-pill-btn:hover,
.score-box .topbar-pill-btn:hover {
  border-color: #ffffff !important;
  box-shadow: 0 0 12px rgba(255, 215, 106, 0.5) !important;
  transform: scale(1.05) !important;
}
"""
    css += unified_buttons_override

    # Shrink phaseDisplayPanelHard to scale(0.38)
    old_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 205px !important;
    width: 600px !important;
    transform: scale(0.50) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
    padding: 2px 10px !important;
  }
  .phase-hard-title { font-size: 12px !important; font-weight: bold !important; color: #ffd76a !important; line-height: 1.0 !important; margin: 0 !important; }
  .phase-hard-help { font-size: 9.5px !important; color: #ffe6a0 !important; line-height: 1.0 !important; margin: 0 !important; }"""

    new_phase_css = """  #phaseDisplayPanelHard {
    position: absolute !important;
    top: 0px !important;
    left: 205px !important;
    width: 500px !important;
    transform: scale(0.38) !important;
    transform-origin: top left !important;
    z-index: 999999 !important;
    display: none;
    flex-direction: column !important;
    align-items: center !important;
    padding: 2px 8px !important;
  }
  .phase-hard-title { font-size: 11px !important; font-weight: bold !important; color: #ffd76a !important; line-height: 1.0 !important; margin: 0 !important; }
  .phase-hard-help { font-size: 8.5px !important; color: #ffe6a0 !important; line-height: 1.0 !important; margin: 0 !important; }"""

    css = css.replace(old_phase_css, new_phase_css)

    open(css_path, 'w', encoding='utf-8').write(css)
    print("2. Updated style_v8.css with unified buttons & shrunken phase panel successfully!")

if __name__ == '__main__':
    fix_all_issues()
