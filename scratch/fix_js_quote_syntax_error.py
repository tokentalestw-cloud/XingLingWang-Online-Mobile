# -*- coding: utf-8 -*-
import sys, re

def fix_quote_syntax():
    sys.stdout.reconfigure(encoding='utf-8')
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Clean double quotes inside string assignments
    clean_js_font = "'Microsoft JhengHei', '微軟正黑體', 'Noto Sans TC', sans-serif"

    # Replace bad inline font-family strings
    js_content = js_content.replace(
        'font-family: "Microsoft JhengHei", "微軟正黑體", "Noto Sans TC", "PingFang TC", "Heiti TC", "Outfit", "Roboto", system-ui, sans-serif;',
        f'font-family: {clean_js_font};'
    )

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Fixed quote syntax in static/game_v8.js successfully!")

    # Update cache-buster in static/index.html to v=11.40-fix-quote-syntax-error
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.40-fix-quote-syntax-error', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.40-fix-quote-syntax-error', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_quote_syntax()
