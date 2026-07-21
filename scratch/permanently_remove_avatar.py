# -*- coding: utf-8 -*-
import os, sys, re

def permanently_remove():
    sys.stdout.reconfigure(encoding='utf-8')
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove avatar markup completely
    idx_content = re.sub(r'\s*<div class="guide-avatar-wrap">.*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'comic_host_avatar.*?</div>', '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'午飯社長', '', idx_content)

    # Update cache-buster to v=9.20-permanently-removed-avatar
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.20-permanently-removed-avatar', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.20-permanently-removed-avatar', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Cleaned static/index.html permanently!")

    # Remove comic_host_avatar.png file if exists
    img_path = 'static/comic_host_avatar.png'
    if os.path.exists(img_path):
        try:
            os.remove(img_path)
            print("2. Deleted static/comic_host_avatar.png successfully!")
        except Exception as e:
            print("Could not remove avatar png:", e)

if __name__ == '__main__':
    permanently_remove()
