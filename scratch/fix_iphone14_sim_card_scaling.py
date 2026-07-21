# -*- coding: utf-8 -*-
import sys, re

def fix_iphone14_card_scaling():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean old sim CSS if present
    block_marker = "/* ==========================================================================\n   IPHONE 14 LANDSCAPE SIMULATOR"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    scaled_sim_css = """/* ==========================================================================
   IPHONE 14 LANDSCAPE SIMULATOR (縮小比例滿版 fit 844px x 390px)
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
  margin: 16px auto !important;
  border-radius: 44px !important;
  border: 12px solid #1c1c1e !important;
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

/* 縮小棋盤與卡牌比例至 58% (全貌完整放入 iPhone 14 視窗) */
body.xlw-iphone14-sim-active .board-wrap,
body.xlw-iphone14-sim-active #boardWrap {
  zoom: 0.58 !important;
  transform-origin: top center !important;
}

@supports not (zoom: 0.58) {
  body.xlw-iphone14-sim-active .board-wrap,
  body.xlw-iphone14-sim-active #boardWrap {
    transform: scale(0.58) !important;
    transform-origin: top center !important;
  }
}

"""

    css_content += scaled_sim_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with iPhone 14 58% board scaling successfully!")

    # Update cache-buster in static/index.html to v=13.80-iphone14-sim-scaled-fit
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.80-iphone14-sim-scaled-fit', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.80-iphone14-sim-scaled-fit', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_iphone14_card_scaling()
