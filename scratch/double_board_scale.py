# -*- coding: utf-8 -*-
import sys, re

def double_scale():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Revert scale(0.45) to scale(0.90) for #boardWrap under landscape media query
    old_line = "transform: translate(-50%, -50%) scale(0.45) !important;"
    new_line = "transform: translate(-50%, -50%) scale(0.90) !important;"

    css_content = css_content.replace(old_line, new_line)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Doubled #boardWrap scale from 0.45 to 0.90 in style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=18.30-board-doubled
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.30-board-doubled', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.30-board-doubled', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    double_scale()
