# -*- coding: utf-8 -*-
import sys, re

def disable_rotate_prompt():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    css_content = open(css_path, encoding='utf-8').read()

    # Replace .xlw-mobile-rotate-prompt to be permanently display: none !important
    old_prompt_base = """/* 直向持握時顯示旋轉提示遮罩 */
.xlw-mobile-rotate-prompt {
  display: none;"""

    new_prompt_base = """/* 直向持握時顯示旋轉提示遮罩 */
.xlw-mobile-rotate-prompt {
  display: none !important;"""

    css_content = css_content.replace(old_prompt_base, new_prompt_base)

    # Remove the media query that displays the prompt in portrait mode
    old_portrait_display = """@media (max-width: 900px) and (orientation: portrait) {
  .xlw-mobile-rotate-prompt {
    display: flex !important;
  }
}"""

    # We replace it with a commented out version or just empty space
    css_content = css_content.replace(old_portrait_display, "/* Rotation prompt disabled on portrait mobile */")

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Disabled portrait rotate prompt in style_v8.css successfully!")

    # 2. Update cache-buster in static/index.html to v=19.70-no-rotate-prompt
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.70-no-rotate-prompt', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.70-no-rotate-prompt', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    disable_rotate_prompt()
