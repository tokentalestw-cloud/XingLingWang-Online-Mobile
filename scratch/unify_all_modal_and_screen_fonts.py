# -*- coding: utf-8 -*-
import sys, re

def unify_fonts():
    sys.stdout.reconfigure(encoding='utf-8')

    clean_font = '"Microsoft JhengHei", "微軟正黑體", "Noto Sans TC", "PingFang TC", "Heiti TC", "Outfit", "Roboto", system-ui, sans-serif'

    # 1. Update static/index.html
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    idx_content = re.sub(r'font-family:\s*\'Cinzel\',\s*serif;?', f'font-family: {clean_font};', idx_content)
    idx_content = re.sub(r'font-family:\s*\'Outfit\',\s*sans-serif;?', f'font-family: {clean_font};', idx_content)

    # Update cache-buster to v=11.30-unified-typography-all-screens
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.30-unified-typography-all-screens', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.30-unified-typography-all-screens', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Updated static/index.html typography cleanly!")

    # 2. Update static/game_v8.js
    js_path = 'static/game_v8.js'
    js_content = open(js_path, encoding='utf-8').read()

    js_content = re.sub(r'font-family:\s*\'Cinzel\',\s*serif;?', f'font-family: {clean_font};', js_content)
    js_content = re.sub(r'font-family:\s*\'Outfit\',\s*sans-serif;?', f'font-family: {clean_font};', js_content)
    js_content = re.sub(r'font-family:\s*sans-serif;?', f'font-family: {clean_font};', js_content)
    js_content = re.sub(r'font-family:\s*\'Courier New\',\s*monospace;?', f'font-family: {clean_font};', js_content)

    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Updated static/game_v8.js typography cleanly!")

    # 3. Update static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    css_content = re.sub(r'font-family:\s*\'Cinzel\',\s*serif\s*!important;?', f'font-family: {clean_font} !important;', css_content)
    css_content = re.sub(r'font-family:\s*\'Outfit\',\s*sans-serif;?', f'font-family: {clean_font};', css_content)

    unify_css_block = f"""

/* ==========================================================================
   STRICT UNIFIED TYPOGRAPHY ACROSS ALL MODALS, OVERLAYS & JUMP SCREENS
   (確保全遊戲所有彈窗、對話框、選單與跳轉畫面 100% 統一字體格式)
   ========================================================================== */

* {{
  font-family: {clean_font} !important;
}}

html, body, div, span, applet, object, iframe,
h1, h2, h3, h4, h5, h6, p, blockquote, pre,
a, abbr, acronym, address, big, cite, code,
del, dfn, em, img, ins, kbd, q, s, samp,
small, strike, strong, sub, sup, tt, var,
b, u, i, center, dl, dt, dd, ol, ul, li,
fieldset, form, label, legend, table, caption,
tbody, tfoot, thead, tr, th, td, article, aside,
canvas, details, embed, figure, figcaption, footer,
header, hgroup, menu, nav, output, ruby, section,
summary, time, mark, audio, video, input, textarea,
select, button,
.modal, .modal-content, .modal-header, .modal-body, .score-panel,
.score-box, .confirm-box, .xlw-modal-overlay, .xlw-choice-modal,
.xlw-chain-overlay, .xlw-spell-activation-overlay, .xlw-tribute-activation-overlay,
#xlwResultPanel, #xlwCorsWarningOverlay, #xlwDebugPanel, #multiplayerLobby {{
  font-family: {clean_font} !important;
}}

"""

    css_content += unify_css_block
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("3. Updated static/style_v8.css with strict unified typography block successfully!")

if __name__ == '__main__':
    unify_fonts()
