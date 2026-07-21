# -*- coding: utf-8 -*-
import sys, re

def apply_clean_rounded_font():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # Modern rounded yet crystal-clear legible sans font stack
    clean_font = '"Microsoft JhengHei", "微軟正黑體", "Noto Sans TC", "PingFang TC", "Heiti TC", "Outfit", "Roboto", system-ui, sans-serif'

    # Replace previous KaiTi font occurrences
    css_content = css_content.replace(
        '"BiauKai", "標楷體", "DFKai-SB", "KaiTi", "Microsoft JhengHei", "Noto Sans TC", system-ui, sans-serif',
        clean_font
    )

    # Clean previous typography block if appended
    block_marker = "/* ==========================================================================\n   SMOOTH KAITI TYPOGRAPHY"
    if block_marker in css_content:
        css_content = css_content[:css_content.find(block_marker)]

    clean_typo_css = f"""/* ==========================================================================
   MODERN CLEAN ROUNDED SANS TYPOGRAPHY (微軟正黑體 / NOTO SANS 高清晰介面字體)
   ========================================================================== */

* {{
  font-family: {clean_font} !important;
}}

html, body, button, select, input, textarea, div, span, p, h1, h2, h3, h4, h5, h6,
#status, .status-bar, .topbar, .score-badge-fixed, #xlwEnemyInfoPanel, #stableActionPanel, .confirm-box {{
  font-family: {clean_font} !important;
}}

/* 高清晰文字對比與微環境陰影 */
.topbar button, .topbar select, .topbar a button,
#endTurnBtn, .end-turn-btn,
#stableActionTactical, #stableActionAttack, #stableActionConfirm, #stableActionCancel,
#status, .enemy-info-title, .score-badge-label, .score-badge-num, .score-val,
.xlw-spell-activation-title, .xlw-tribute-activation-title, .xlw-coin-toss-title, .xlw-coin-toss-status-bar {{
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.8) !important;
  letter-spacing: 0.4px !important;
}}

"""

    css_content += clean_typo_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with modern clean rounded sans typography successfully!")

    # Update cache-buster in static/index.html to v=11.20-clean-rounded-sans-typography
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.20-clean-rounded-sans-typography', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.20-clean-rounded-sans-typography', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_clean_rounded_font()
