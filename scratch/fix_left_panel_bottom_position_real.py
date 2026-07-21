# -*- coding: utf-8 -*-
import sys, re

def fix_panel_real_bottom():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # 1. Clean previous RESTORE LEFT CARD PREVIEW block if appended
    block_marker = "/* ==========================================================================\n   RESTORE LEFT CARD PREVIEW"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    real_bottom_css = """/* ==========================================================================
   FORCE RESTORE LEFT CARD PREVIEW PANEL ORIGINAL LOWER POSITION
   (徹底修復：強制將左側卡牌放大預覽視窗降至底部原本位置 bottom: 20px)
   ========================================================================== */

.xlw-left-card-panel, #xlwLeftCardPanel {
  position: absolute !important;
  top: auto !important;
  bottom: 20px !important;
}

@media (max-width: 1500px) {
  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    top: auto !important;
    bottom: 20px !important;
  }
}

@media (max-width: 900px) {
  .xlw-left-card-panel, #xlwLeftCardPanel {
    position: fixed !important;
    top: auto !important;
    bottom: 15px !important;
  }
}

"""

    css_content += real_bottom_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css to force bottom: 20px across all media queries successfully!")

    # Update cache-buster in static/index.html to v=12.30-fix-left-panel-bottom-real
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.30-fix-left-panel-bottom-real', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.30-fix-left-panel-bottom-real', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_panel_real_bottom()
