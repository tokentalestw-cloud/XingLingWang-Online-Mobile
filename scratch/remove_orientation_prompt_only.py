# -*- coding: utf-8 -*-
import sys, re

def remove_prompt_only():
    sys.stdout.reconfigure(encoding='utf-8')

    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # Remove orientation prompt HTML overlay
    clean_html_pattern = r'\s*<!-- 螢幕直向時的轉橫向提示遮罩 \(Rotate to Landscape Prompt Overlay\) -->\s*<div id="xlwOrientationOverlay" class="xlw-orientation-overlay">.*?</div>\s*</div>'
    idx_content = re.sub(clean_html_pattern, '', idx_content, flags=re.DOTALL)
    
    # Fallback absolute removal
    if 'xlwOrientationOverlay' in idx_content:
        start_idx = idx_content.find('<!-- 螢幕直向時的轉橫向提示遮罩')
        if start_idx >= 0:
            end_idx = idx_content.find('</div>\n  </div>', start_idx)
            if end_idx >= 0:
                idx_content = idx_content[:start_idx] + idx_content[end_idx + 14:]

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Removed orientation prompt HTML overlay from static/index.html successfully!")

    # Remove orientation prompt CSS from style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    block_marker = "/* ==========================================================================\n   ROTATE TO LANDSCAPE PROMPT OVERLAY"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Removed orientation prompt CSS from static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=15.70-remove-orientation-prompt
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=15.70-remove-orientation-prompt', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=15.70-remove-orientation-prompt', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    remove_prompt_only()
