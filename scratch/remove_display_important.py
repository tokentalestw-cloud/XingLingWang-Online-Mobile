# -*- coding: utf-8 -*-
import sys, re

def remove_important():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Locate the display rule for .xlw-welcome-overlay and strip the !important flag
    old_overlay_rule = "display: flex !important;"
    # Let's target it specifically within the welcome overlay block
    css_content = css_content.replace(
        "display: flex !important;\n  align-items: center !important;\n  justify-content: center !important;\n  overflow: hidden !important;\n  font-family: \"Microsoft JhengHei\"",
        "display: flex;\n  align-items: center !important;\n  justify-content: center !important;\n  overflow: hidden !important;\n  font-family: \"Microsoft JhengHei\""
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Removed !important from welcome overlay display rule in style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=17.70-display-bug-fixed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.70-display-bug-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.70-display-bug-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    remove_important()
