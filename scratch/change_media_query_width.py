# -*- coding: utf-8 -*-
import sys, re

def change_query():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Replace all matches of max-width: 1024px landscape to 1400px
    old_query = "@media (max-width: 1024px) and (orientation: landscape)"
    new_query = "@media (max-width: 1400px) and (orientation: landscape)"

    css_content = css_content.replace(old_query, new_query)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Replaced landscape media query thresholds to 1400px in style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=18.10-media-query-widened
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=18.10-media-query-widened', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=18.10-media-query-widened', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    change_query()
