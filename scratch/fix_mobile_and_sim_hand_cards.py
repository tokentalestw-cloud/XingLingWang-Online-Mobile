# -*- coding: utf-8 -*-
import sys, re

def fix_mobile_hand_cards():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    hand_fit_css = """

/* ==========================================================================
   MOBILE & IPHONE 14 HAND CARD FAN-OUT & PERFECT FIT
   (手機與模擬器手牌 100% 完整無縫顯示，重疊扇形展開不超出邊界)
   ========================================================================== */

/* 1. iPhone 14 模擬器手牌適配 */
body.xlw-iphone14-sim-active .hand-panel {
  max-width: 100% !important;
  overflow: hidden !important;
}

body.xlw-iphone14-sim-active .hand {
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  gap: 2px !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  max-width: 100% !important;
  padding: 4px 10px !important;
  -webkit-overflow-scrolling: touch !important;
}

body.xlw-iphone14-sim-active .hand .card {
  width: 100px !important;
  height: 140px !important;
  min-width: 80px !important;
  flex-shrink: 1 !important;
  margin-left: -14px !important;
  transition: transform 0.2s ease, z-index 0.2s ease !important;
}

body.xlw-iphone14-sim-active .hand .card:first-child {
  margin-left: 0 !important;
}

body.xlw-iphone14-sim-active .hand .card:hover,
body.xlw-iphone14-sim-active .hand .card:active {
  z-index: 200 !important;
  transform: translateY(-20px) scale(1.18) !important;
}

/* 2. 手機版 RWD 實機 (width <= 900px) 手牌無縫適配 */
@media (max-width: 900px) {
  .hand-panel {
    max-width: 100% !important;
    overflow: hidden !important;
  }
  .hand {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    gap: 2px !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    max-width: 100% !important;
    padding: 4px 6px !important;
    -webkit-overflow-scrolling: touch !important;
  }
  .hand .card {
    width: 95px !important;
    height: 132px !important;
    min-width: 75px !important;
    flex-shrink: 1 !important;
    margin-left: -16px !important;
    transition: transform 0.2s ease, z-index 0.2s ease !important;
  }
  .hand .card:first-child {
    margin-left: 0 !important;
  }
  .hand .card:hover,
  .hand .card:active {
    z-index: 200 !important;
    transform: translateY(-18px) scale(1.2) !important;
  }
}

"""

    css_content += hand_fit_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with mobile hand card fan-out & fit CSS successfully!")

    # Update cache-buster in static/index.html to v=14.90-mobile-hand-cards-fit
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=14.90-mobile-hand-cards-fit', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=14.90-mobile-hand-cards-fit', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_mobile_hand_cards()
