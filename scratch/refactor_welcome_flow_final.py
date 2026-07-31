# -*- coding: utf-8 -*-
import sys, re

def refactor_welcome_flow():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'
    deck_path = 'static/deck_builder.html'

    # 1. Update static/index.html to remove the mode-group buttons completely and add "🏠 返回首頁" button
    idx_content = open(idx_path, encoding='utf-8').read()

    # Regex to completely delete the mode-group container
    idx_content = re.sub(
        r'<div class="topbar-group mode-group"[^>]*>.*?</div>\s*</div>',
        '',
        idx_content,
        flags=re.DOTALL
    )

    # Let's ensure the Back to Home Screen button is in the topbar settings group
    # Rename "🏠 返回主選單" to "🏠 返回首頁"
    idx_content = idx_content.replace('🏠 返回主選單', '🏠 返回首頁')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Removed mode-group buttons from index.html and configured '🏠 返回首頁' button successfully!")

    # 2. Update static/deck_builder.html to add "🏠 返回首頁" button
    deck_content = open(deck_path, encoding='utf-8').read()
    
    # Replace "返回對戰大廳" with "🏠 返回首頁"
    deck_content = deck_content.replace(
        '<a href="/" class="top-nav-btn">返回對戰大廳</a>',
        '<a href="/" class="top-nav-btn" style="border-color: #ffd76a; color: #ffd76a; font-weight: bold;">🏠 返回首頁</a>'
    )
    
    open(deck_path, 'w', encoding='utf-8').write(deck_content)
    print("2. Added '🏠 返回首頁' navigation to deck_builder.html successfully!")

    # 3. Update static/style_v8.css to hide .xlw-mobile-fs-banner completely
    css_content = open(css_path, encoding='utf-8').read()

    # Force hide the browser banner to remove any fullscreen prompt
    css_content = css_content.replace(
        ".xlw-mobile-fs-banner {\n  display: none;",
        ".xlw-mobile-fs-banner {\n  display: none !important;"
    )
    
    # Also find the media query block matching .xlw-mobile-fs-banner and set to none
    css_content = re.sub(
        r'\.xlw-mobile-fs-banner\s*\{\s*display:\s*flex\s*!important;\s*\}',
        '.xlw-mobile-fs-banner { display: none !important; }',
        css_content
    )

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Disabled full-screen browser banner in style_v8.css successfully!")

    # 4. Update cache-buster in static/index.html to v=17.20-welcome-flow-refactored
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.20-welcome-flow-refactored', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.20-welcome-flow-refactored', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("4. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    refactor_welcome_flow()
