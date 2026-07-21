# -*- coding: utf-8 -*-
import sys, re

def remove_redundant_elements():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove xlwMangaGuideCorner HTML
    guide_pattern = r'<!-- 右下角漫畫社長引導對話框 -->\s*<div id="xlwMangaGuideCorner".*?</div>\s*</div>'
    idx_content = re.sub(guide_pattern, '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'<div id="xlwMangaGuideCorner".*?</div>\s*</div>', '', idx_content, flags=re.DOTALL)

    # Remove arcade-quote-bubble from index.html
    quote_pattern = r'<!-- 底部對話說明對話框 -->\s*<div class="arcade-quote-bubble">.*?</div>\s*</div>'
    idx_content = re.sub(quote_pattern, '', idx_content, flags=re.DOTALL)
    idx_content = re.sub(r'<div class="arcade-quote-bubble">.*?</div>', '', idx_content, flags=re.DOTALL)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Removed manga host guide and card quote bubble from static/index.html successfully!")

    # 2. Update game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    # Remove cardQuoteTag & cardEffectText logic from showModal
    js_content = re.sub(r'const cardQuoteTag = \$\(["\']leftCardQuoteTag["\']\);.*?cardEffectText\.textContent = .*?;\s*', '', js_content, flags=re.DOTALL)

    # Remove guideText logic from setStatus
    js_content = re.sub(r'const guideText = \$\(["\']mangaGuideText["\']\);.*?if \(guideText && t\) \{\s*guideText\.textContent = t;\s*\}', '', js_content, flags=re.DOTALL)

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Removed quote bubble & guide avatar JS logic from static/game_v8.js successfully!")

    # 3. Update style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Remove quote bubble & manga guide CSS blocks
    css_content = re.sub(r'/\* 底部對話說明框 \*/.*?/\* ==========================================================================\s*MANGA GUIDE CORNER', '/* ==========================================================================\n   MANGA GUIDE CORNER', css_content, flags=re.DOTALL)
    css_content = re.sub(r'/\* ==========================================================================\s*MANGA GUIDE CORNER.*?\*/.*?(?=/\* ==========================================================================\s*SLOTS & CARDS)', '', css_content, flags=re.DOTALL)

    # Adjust panel height if quote bubble is removed
    css_content = css_content.replace('height: 620px !important;', 'height: 520px !important;')

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Removed quote bubble & manga guide CSS from static/style_v8.css successfully!")

if __name__ == '__main__':
    remove_redundant_elements()
