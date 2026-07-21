# -*- coding: utf-8 -*-
import sys, re

def fix_broken_image():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Replace leftPanelImg with proper default src and onerror fallback
    idx_content = idx_content.replace(
        '<img id="leftPanelImg" src="" alt="card detail image">',
        '<img id="leftPanelImg" src="/static/card_back.jpeg" alt="card detail image" onerror="this.onerror=null;this.src=\'/static/card_back.jpeg\';">'
    )

    # Update cache-buster to v=9.35-image-fallback-fix
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.35-image-fallback-fix', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.35-image-fallback-fix', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html with image fallback successfully!")

    # 2. Update showModal in static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    old_img_set = 'leftImg.src = card.image || "/static/little_traveler.jpeg";'
    new_img_set = """leftImg.onerror = function() {
      this.onerror = null;
      this.src = "/static/card_back.jpeg";
    };
    leftImg.src = (card && card.image) ? card.image : "/static/card_back.jpeg";"""

    if old_img_set in js_content:
        js_content = js_content.replace(old_img_set, new_img_set)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Updated showModal in static/game_v8.js with image fallback successfully!")
    else:
        print("old_img_set string not found directly, performing regex replacement...")
        js_content = re.sub(r'leftImg\.src = card\.image \|\| [^;]+;', new_img_set, js_content)
        open(js_path, 'w', encoding='utf-8').write(js_content)
        print("2. Updated showModal in static/game_v8.js via regex successfully!")

if __name__ == '__main__':
    fix_broken_image()
