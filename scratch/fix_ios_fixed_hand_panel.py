# -*- coding: utf-8 -*-
import sys, re

def fix_fixed_hand_panel():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Replace position: absolute !important; with position: fixed !important; inside .hand-panel in the landscape block
    old_block = """  /* 8. 懸浮 3D 立體我方手牌區 (懸浮高度拉升至 bottom: 14px，保證在戰場之上 100% 完整露出) */
  .hand-panel {
    position: absolute !important;
    bottom: 14px !important;"""

    new_block = """  /* 8. 懸浮 3D 立體我方手牌區 (懸浮高度拉升至 bottom: 14px，保證在戰場之上 100% 完整露出) */
  .hand-panel {
    position: fixed !important;
    bottom: 14px !important;"""

    if old_block in css_content:
        css_content = css_content.replace(old_block, new_block)
    else:
        # Fallback regex replace for any position style under .hand-panel in that block
        css_content = re.sub(
            r'\.hand-panel\s*\{\s*position:\s*absolute\s*!important;',
            '.hand-panel {\n    position: fixed !important;',
            css_content
        )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css to use position: fixed !important; for hand-panel successfully!")

    # Update cache-buster in static/index.html to v=16.30-ios-fixed-hand-panel
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=16.30-ios-fixed-hand-panel', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=16.30-ios-fixed-hand-panel', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_fixed_hand_panel()
