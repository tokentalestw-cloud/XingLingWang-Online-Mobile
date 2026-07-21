# -*- coding: utf-8 -*-
import sys, re

def make_full_slot():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Clean previous standee rule block at end of file if exists
    block_marker = "/* ==========================================================================\n   FOREST STANDEE CONTAINMENT & LEFT PANEL OPACITY FIX"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    new_full_slot_css = """/* ==========================================================================
   FOREST STANDEE FULL-SLOT SIZING & LEFT PANEL OPACITY FIX
   (將森林區小旅人圖片調至與戰場格子完全等大 100% 填滿)
   ========================================================================== */

#playerForest, #enemyForest {
  overflow: hidden !important;
  position: relative !important;
}

.traveler-3d-standee {
  width: 100% !important;
  height: 100% !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  transform: none !important;
  pointer-events: none !important;
  z-index: 1 !important;
}

.traveler-3d-img {
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  border-radius: 8px !important;
  display: block !important;
}

.forest-3d-overlay {
  position: absolute !important;
  bottom: 0 !important;
  left: 0 !important;
  right: 0 !important;
  background: rgba(10, 8, 8, 0.78) !important;
  color: #ffe6a0 !important;
  font-size: 11px !important;
  font-weight: bold !important;
  padding: 3px 2px !important;
  text-align: center !important;
  border-top: 1.5px solid rgba(0, 255, 127, 0.6) !important;
  z-index: 3 !important;
  pointer-events: none !important;
}

.xlw-left-card-panel {
  background: #0c080e !important;
  z-index: 10050 !important;
  box-shadow: 0 12px 50px rgba(0, 0, 0, 0.98), 0 0 25px rgba(255, 230, 0, 0.4) !important;
}

.xlw-left-card-panel .panel-inner {
  position: relative !important;
  z-index: 2 !important;
  background: #0c080e !important;
}
"""

    css_content += new_full_slot_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with full-slot Little Traveler sizing successfully!")

    # Update cache-buster in static/index.html to v=9.70-forest-traveler-full-slot
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.70-forest-traveler-full-slot', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.70-forest-traveler-full-slot', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    make_full_slot()
