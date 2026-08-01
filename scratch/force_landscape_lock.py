# -*- coding: utf-8 -*-
import sys, re

def force_landscape():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Disable portrait media queries by changing them to a non-matching condition (max-width: 0px)
    css_content = css_content.replace(
        "@media (max-width: 1024px) and (orientation: portrait)",
        "@media (max-width: 0px)"
    )
    css_content = css_content.replace(
        "@media (max-width: 900px) and (orientation: portrait)",
        "@media (max-width: 0px)"
    )

    # 2. Generalize landscape media queries so they match when rotated
    css_content = css_content.replace(
        "@media (max-width: 1400px) and (orientation: landscape)",
        "@media (max-width: 1400px)"
    )

    # 3. Append the orientation-lock CSS rotation to the tail of the stylesheet
    orientation_lock = """

/* ===== 完美強制橫向螢幕鎖定 (Physical Orientation Lock to Landscape) ===== */
@media (orientation: portrait) {
  html {
    width: 100vw !important;
    height: 100vh !important;
    overflow: hidden !important;
    position: fixed !important;
  }
  body {
    width: 100vh !important;
    height: 100vw !important;
    position: fixed !important;
    top: 0 !important;
    left: 100vw !important;
    transform: rotate(90deg) !important;
    transform-origin: top left !important;
    overflow: hidden !important;
  }
}
"""

    css_content += orientation_lock

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Successfully modified style_v8.css to force lock landscape orientation!")

    # 4. Update cache-buster in static/index.html to v=19.80-landscape-lock-done
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.80-landscape-lock-done', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.80-landscape-lock-done', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    force_landscape()
