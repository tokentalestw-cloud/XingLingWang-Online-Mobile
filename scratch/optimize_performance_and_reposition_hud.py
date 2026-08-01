# -*- coding: utf-8 -*-
import sys, re

def optimize_and_reposition():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # 1. Reposition #xlwEnemyInfoPanel under mobile landscape media query
    # Shift it from left: 180px, top: 32px to left: 8px, top: 85px
    old_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 180px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
  }"""

    new_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 8px !important;
    top: 85px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.95) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # 2. Performance optimization: remove heavy backdrop-filters from active gameplay elements
    # Remove backdrop-filter from .board
    css_content = css_content.replace(
        "background-color: rgba(16, 12, 32, 0.82) !important; /* Premium dark cosmic obsidian glass board */\n  backdrop-filter: blur(16px);",
        "background-color: rgba(12, 8, 22, 0.96) !important; /* Premium dark cosmic obsidian glass board */"
    )
    # Remove backdrop-filter from card details or slot classes where it degrades active scroll/drag performance
    css_content = re.sub(r'backdrop-filter:\s*blur\(16px\)\s*!important;', 'background-color: rgba(15, 10, 25, 0.96) !important;', css_content)
    css_content = re.sub(r'backdrop-filter:\s*blur\(12px\);', 'background-color: rgba(15, 10, 25, 0.96);', css_content)
    css_content = re.sub(r'backdrop-filter:\s*blur\(10px\);', '', css_content)
    css_content = re.sub(r'backdrop-filter:\s*blur\(4px\);', '', css_content)

    # 3. Add hardware acceleration to active animation classes (.card, .slot, .zone, .bouncing-mascot)
    gpu_optimization = """
/* ===== GPU Hardware Acceleration and Performance Optimization ===== */
.card, .slot, .zone, .bouncing-mascot, #boardWrap, .traveler-3d-img {
  transform: translate3d(0, 0, 0);
  will-change: transform;
  backface-visibility: hidden;
  perspective: 1000px;
}
"""
    css_content += gpu_optimization

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Repositioned opponent hand badge and optimized CSS rendering performance in style_v8.css successfully!")

    # 4. Update cache-buster in static/index.html to v=20.00-performance-optimized
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=20.00-performance-optimized', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=20.00-performance-optimized', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    optimize_and_reposition()
