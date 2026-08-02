# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    js_path = os.path.join(base_dir, 'static', 'game_v8.js')
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/game_v8.js: Increase rotateDeg multiplier for wider fan spread
    js_content = open(js_path, encoding='utf-8').read()

    old_rot = "const rotateDeg = (offset * 3.5).toFixed(1);"
    new_rot = "const rotateDeg = (offset * 5.2).toFixed(1);"

    js_content = js_content.replace(old_rot, new_rot)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Updated game_v8.js with wider fan rotation multiplier (5.2) successfully!")

    # 2. Update static/style_v8.css: Shift board upward by 50 units & set margin-left to -20px for wider fan
    css_content = open(css_path, encoding='utf-8').read()

    css_content = css_content.replace(
        'top: calc(50% + 50px) !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;',
        'top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;'
    )

    css_content = css_content.replace(
        'top: calc(30% + 50px) !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;',
        'top: 30% !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;'
    )

    # Adjust card back overlap margin from -26px to -20px for wider fan spread
    css_content = css_content.replace(
        'margin-left: -26px !important;',
        'margin-left: -20px !important;'
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Updated style_v8.css board top positioning (-50px) & wider fan margin (-20px) successfully!")

    # 3. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.80-board-up-50-more-wider-fan-hand', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.80-board-up-50-more-wider-fan-hand', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
