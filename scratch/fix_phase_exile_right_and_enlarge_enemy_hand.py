# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/index.html: Move #phaseDisplayPanelHard INSIDE .board
    idx_content = open(idx_path, encoding='utf-8').read()

    phase_panel_html = '<div id="phaseDisplayPanelHard" class="phase-display-panel-hard" style="display: none !important;">\n    <div class="phase-hard-title">目前階段：<span id="xlwPhaseTitleText">準備階段</span></div>\n    <div class="phase-hard-help" id="xlwPhaseHelpText">準備階段：抽取卡牌與重置資源...</div>\n  </div>'

    # Remove phase panel from topbar
    idx_content = idx_content.replace(phase_panel_html, '')

    # Insert phase panel inside #board right after #playerExile
    board_exile_tag = '<div id="playerExile" class="exile-zone" title="我方除外區"></div>'
    idx_content = idx_content.replace(board_exile_tag, board_exile_tag + '\n    ' + phase_panel_html)

    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.20-phase-exile-right-and-large-enemy-hand', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.20-phase-exile-right-and-large-enemy-hand', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Moved #phaseDisplayPanelHard inside .board in index.html successfully!")

    # 2. Update static/style_v8.css: High-priority #phaseDisplayPanelHard rule & enlarge enemy floating cards to 78x108
    css_content = open(css_path, encoding='utf-8').read()

    # Override all #phaseDisplayPanelHard selectors
    css_content = re.sub(
        r'body\.xlw-iphone14-sim-active \.game-shell #phaseDisplayPanelHard\s*\{[^}]*\}',
        '',
        css_content
    )

    old_phase_rule = r'#phaseDisplayPanelHard\s*\{[^}]*\}'
    
    new_phase_rule = """body #phaseDisplayPanelHard,
body.xlw-iphone14-sim-active #phaseDisplayPanelHard,
body.xlw-iphone14-sim-active .game-shell #phaseDisplayPanelHard,
.board #phaseDisplayPanelHard,
#phaseDisplayPanelHard {
  position: absolute !important;
  top: 467.5px !important;
  right: 150px !important;
  left: auto !important;
  width: 160px !important;
  max-width: 160px !important;
  transform: scale(0.90) !important;
  transform-origin: top left !important;
  z-index: 999999 !important;
  display: none;
  flex-direction: column !important;
  align-items: center !important;
  padding: 6px 10px !important;
  background: rgba(12, 8, 22, 0.95) !important;
  border: 1.5px solid rgba(255, 215, 106, 0.5) !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.8) !important;
}"""

    css_content = re.sub(old_phase_rule, new_phase_rule, css_content)

    # Update enemy floating hand cards size to 78px x 108px (matching player hand cards!)
    old_floating_css = """.floating-enemy-card-back {
  width: 28px !important;
  height: 42px !important;
  object-fit: cover !important;
  border-radius: 3px !important;
  border: 0.5px solid rgba(255, 215, 106, 0.4) !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.6) !important;
  margin-left: -12px !important;
  transition: all 0.2s ease !important;
}"""

    new_floating_css = """.floating-enemy-card-back {
  width: 78px !important;
  height: 108px !important;
  object-fit: cover !important;
  border-radius: 6px !important;
  border: 1.5px solid rgba(255, 215, 106, 0.5) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.8), 0 0 10px rgba(255, 215, 106, 0.2) !important;
  margin-left: -35px !important;
  transition: all 0.2s ease !important;
}"""

    css_content = css_content.replace(old_floating_css, new_floating_css)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated style_v8.css high-priority phase position & 78x108 enemy hand cards successfully!")

if __name__ == '__main__':
    apply_fixes()
