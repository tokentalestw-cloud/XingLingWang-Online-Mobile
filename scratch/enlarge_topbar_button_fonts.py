# -*- coding: utf-8 -*-
import sys, re

def enlarge_topbar_fonts():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Enlarge topbar container, buttons, dropdowns, and group labels
    css_content = css_content.replace(
      "height: 52px !important;",
      "height: 58px !important;"
    )
    css_content = css_content.replace(
      "font-size: 13px !important;\n  font-weight: 900 !important;\n  white-space: nowrap !important;\n}",
      "font-size: 14.5px !important;\n  font-weight: 900 !important;\n  white-space: nowrap !important;\n}"
    )

    enlarged_topbar_css = """

/* ==========================================================================
   ENLARGED & COMFORTABLY LEGIBLE TOPBAR BUTTON FONTS
   (放大最上排按鈕與選單字體，確保清晰好辨識)
   ========================================================================== */

.topbar-grouped-v9 {
  height: 58px !important;
  padding: 0 20px !important;
  gap: 12px !important;
}

.topbar-group {
  gap: 8px !important;
  padding: 5px 10px !important;
}

.group-label {
  font-size: 14.5px !important;
}

.topbar-group select {
  font-size: 14.5px !important;
  padding: 5px 12px !important;
}

.topbar-action-btn {
  font-size: 14.5px !important;
  padding: 7px 16px !important;
  font-weight: 900 !important;
  letter-spacing: 0.4px !important;
}

.topbar-setting-btn, .topbar-setting-select {
  font-size: 14px !important;
  padding: 6px 14px !important;
  font-weight: 900 !important;
}

"""

    css_content += enlarged_topbar_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with enlarged topbar button fonts successfully!")

    # Update cache-buster in static/index.html to v=13.50-enlarged-topbar-button-fonts
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.50-enlarged-topbar-button-fonts', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.50-enlarged-topbar-button-fonts', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    enlarge_topbar_fonts()
