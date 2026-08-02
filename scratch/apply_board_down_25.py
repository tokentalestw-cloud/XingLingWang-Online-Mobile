# -*- coding: utf-8 -*-
import os, sys, re

def apply_fixes():
    sys.stdout.reconfigure(encoding='utf-8')

    base_dir = os.getcwd()
    css_path = os.path.join(base_dir, 'static', 'style_v8.css')
    idx_path = os.path.join(base_dir, 'static', 'index.html')

    # 1. Update static/style_v8.css: Shift board downward by 25 units (top: calc(50% + 25px) / calc(30% + 25px))
    css_content = open(css_path, encoding='utf-8').read()

    css_content = css_content.replace(
        'top: 50% !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;',
        'top: calc(50% + 25px) !important;\n  left: 50% !important;\n  transform: translate(-50%, -50%) scale(0.44) !important;'
    )

    css_content = css_content.replace(
        'top: 30% !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;',
        'top: calc(30% + 25px) !important;\n    left: 50% !important;\n    transform: translate(-42.5%, -50%) scale(0.46) !important;'
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated style_v8.css board top positioning (+25px downward) successfully!")

    # 2. Update index.html cache-buster
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=21.90-board-shifted-down-25', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=21.90-board-shifted-down-25', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_fixes()
