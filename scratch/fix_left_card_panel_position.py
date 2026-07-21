# -*- coding: utf-8 -*-
import sys, re

def fix_panel_position():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    panel_pos_css = """

/* ==========================================================================
   RESTORE LEFT CARD PREVIEW PANEL ORIGINAL LOWER POSITION
   (卡牌放大預覽圖移回原本位於下方的舒適原位)
   ========================================================================== */

.xlw-left-card-panel, #xlwLeftCardPanel {
  top: auto !important;
  bottom: 24px !important;
}

"""

    css_content += panel_pos_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Restored left card panel original lower position in static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=12.20-fix-left-card-panel-position
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.20-fix-left-card-panel-position', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.20-fix-left-card-panel-position', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_panel_position()
