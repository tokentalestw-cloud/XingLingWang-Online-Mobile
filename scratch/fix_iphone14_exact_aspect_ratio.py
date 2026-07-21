# -*- coding: utf-8 -*-
import sys, re

def fix_iphone14_aspect_ratio():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    exact_aspect_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (100% 精準 19.5:9 比例 844px x 390px 內部視窗)
   ========================================================================== */

body.xlw-iphone14-sim-active {
  background: radial-gradient(circle at 50% 50%, #1c152a 0%, #07050a 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
}

body.xlw-iphone14-sim-active .game-shell {
  width: 844px !important;
  height: 390px !important;
  min-width: 844px !important;
  min-height: 390px !important;
  max-width: 844px !important;
  max-height: 390px !important;
  margin: 20px auto !important;
  box-sizing: content-box !important;
  border-radius: 44px !important;
  border: 14px solid #1c1c1e !important;
  outline: 2px solid #2c2c2e !important;
  box-shadow: 
    0 25px 70px rgba(0, 0, 0, 0.95),
    0 0 35px rgba(255, 215, 106, 0.3) !important;
  overflow: hidden !important;
  position: relative !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

/* 精準適配 19.5:9 內部視窗比例 (52% 棋盤縮放) */
body.xlw-iphone14-sim-active .board-wrap,
body.xlw-iphone14-sim-active #boardWrap {
  zoom: 0.52 !important;
  transform-origin: top center !important;
}

@supports not (zoom: 0.52) {
  body.xlw-iphone14-sim-active .board-wrap,
  body.xlw-iphone14-sim-active #boardWrap {
    transform: scale(0.52) !important;
    transform-origin: top center !important;
  }
}

"""

    css_content += exact_aspect_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with exact 19.5:9 (844px x 390px) aspect ratio successfully!")

    # Update cache-buster in static/index.html to v=13.90-iphone14-exact-19.5-9-aspect
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.90-iphone14-exact-19.5-9-aspect', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.90-iphone14-exact-19.5-9-aspect', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_iphone14_aspect_ratio()
