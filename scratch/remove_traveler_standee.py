# -*- coding: utf-8 -*-
import sys, re

def remove_traveler_standee():
    sys.stdout.reconfigure(encoding='utf-8')

    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove traveler-3d-standee blocks
    idx_content = re.sub(r'\s*<div class="traveler-3d-standee">.*?</div>', '', idx_content, flags=re.DOTALL)

    # Update cache-busters to v=9.40-remove-traveler-standee
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=9.40-remove-traveler-standee', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=9.40-remove-traveler-standee', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Successfully removed traveler-3d-standee from static/index.html!")

if __name__ == '__main__':
    remove_traveler_standee()
