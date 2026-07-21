# -*- coding: utf-8 -*-
import sys, re

def restore_positions():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # 1. Clean previous 3D CARD DECK & GRAVEYARD STACK block if appended
    block_marker = "/* ==========================================================================\n   3D CARD DECK & GRAVEYARD STACK"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    # 2. Append zero-layout-impact 3D stack shadow rules (NO position or transform mutation!)
    safe_stack_css = """/* ==========================================================================
   SAFE 3D STACK LAYER SHADOWS (完全不改變格子定位 position/transform)
   ========================================================================== */

/* 1 層堆疊厚度 */
.xlw-stack-depth-1 {
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 6px rgba(0, 0, 0, 0.75) !important;
}

/* 2 層堆疊厚度 */
.xlw-stack-depth-2 {
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 0 #191026,
    5px 5px 10px rgba(0, 0, 0, 0.85) !important;
}

/* 3 層堆疊厚度 */
.xlw-stack-depth-3 {
  box-shadow: 
    1.5px 1.5px 0 #281d38,
    3px 3px 0 #191026,
    4.5px 4.5px 0 #0f091a,
    6.5px 6.5px 14px rgba(0, 0, 0, 0.9) !important;
}

/* 4 層滿疊厚度 */
.xlw-stack-depth-4 {
  box-shadow: 
    1.5px 1.5px 0 rgba(212, 175, 55, 0.7),
    3px 3px 0 #281d38,
    4.5px 4.5px 0 #191026,
    6px 6px 0 #0f091a,
    8px 8px 18px rgba(0, 0, 0, 0.95) !important;
}

"""

    css_content += safe_stack_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Restored original grid positions in static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=12.50-restore-all-grid-positions
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=12.50-restore-all-grid-positions', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=12.50-restore-all-grid-positions', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    restore_positions()
