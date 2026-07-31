# -*- coding: utf-8 -*-
import sys, re

def fix_button_fonts():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Locate the welcome menu css and replace with larger font and higher contrast
    old_menu_css = """.menu-btn {
  position: relative;
  width: 100%;
  padding: 12px 20px;
  font-size: 16px;
  font-weight: 900;
  border-radius: 50px;
  cursor: pointer;
  border: 2px solid #ffd76a;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
}"""

    new_menu_css = """.menu-btn {
  position: relative;
  width: 100%;
  padding: 14px 24px !important;
  font-size: 22px !important; /* 大幅放大字體 */
  font-weight: 900 !important;
  border-radius: 50px !important;
  cursor: pointer !important;
  border: 3px solid #ffd76a !important; /* 加粗金黃邊框 */
  color: #ffe600 !important; /* 明亮高對比黃色字體 */
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 12px !important;
  overflow: hidden !important;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.95), 0 0 10px rgba(0, 0, 0, 0.9) !important; /* 強力黑色描邊字影 */
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.8) !important;
}"""

    if old_menu_css in css_content:
        css_content = css_content.replace(old_menu_css, new_menu_css)
    else:
        # Fallback regex search
        css_content = re.sub(
            r'\.menu-btn\s*\{[^}]*\}',
            new_menu_css,
            css_content,
            flags=re.DOTALL
        )

    # Make the red button (multiplayer) also high contrast red
    old_multi_css = """.menu-multi {
  background: linear-gradient(135deg, #2b0d18 0%, #6f1b3c 100%) !important;
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.15);
  border-color: #ff4d4f !important;
}"""

    new_multi_css = """.menu-multi {
  background: linear-gradient(135deg, #2b0d18 0%, #6f1b3c 100%) !important;
  box-shadow: 0 4px 15px rgba(255, 77, 79, 0.3) !important;
  border-color: #ff4d4f !important;
  color: #ff6b6b !important; /* 高對比紅字 */
}"""

    if old_multi_css in css_content:
        css_content = css_content.replace(old_multi_css, new_multi_css)

    # Adjust RWD scale of welcome container to prevent shrinking button text on landscape mobile
    old_rwd = """@media (max-width: 1024px) and (orientation: landscape) {
  .welcome-container {
    transform: scale(0.8);
    transform-origin: center center;
    gap: 12px;
  }
}"""

    new_rwd = """@media (max-width: 1024px) and (orientation: landscape) {
  .welcome-container {
    transform: scale(0.92) !important; /* 減少縮放比例，維持按鈕字體清晰 */
    transform-origin: center center !important;
    gap: 10px !important;
  }
  .menu-btn {
    padding: 10px 18px !important;
    font-size: 18px !important; /* 橫屏下微調但依然足夠大 */
  }
}"""

    if old_rwd in css_content:
        css_content = css_content.replace(old_rwd, new_rwd)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css button fonts successfully!")

    # Update cache-buster in static/index.html to v=17.10-welcome-buttons-font-fixed
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.10-welcome-buttons-font-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.10-welcome-buttons-font-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_button_fonts()
