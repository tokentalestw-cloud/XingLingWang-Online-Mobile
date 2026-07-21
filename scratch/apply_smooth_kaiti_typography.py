# -*- coding: utf-8 -*-
import sys, re

def apply_typography():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    # 1. Update font-family in :root and global selectors
    kaiti_font = '"BiauKai", "標楷體", "DFKai-SB", "KaiTi", "Microsoft JhengHei", "Noto Sans TC", system-ui, sans-serif'

    css_content = re.sub(
        r'font-family:\s*system-ui,[^;]+;',
        f'font-family: {kaiti_font} !important;',
        css_content
    )

    # 2. Append smooth KaiTi typography & text-shadow softening rules
    typo_css = f"""

/* ==========================================================================
   SMOOTH KAITI TYPOGRAPHY & EMBOSS REMOVAL (標楷體與柔和高清晰文字系統)
   ========================================================================== */

* {{
  font-family: {kaiti_font} !important;
}}

html, body, button, select, input, textarea, div, span, p, h1, h2, h3, h4, h5, h6,
#status, .status-bar, .topbar, .score-badge-fixed, #xlwEnemyInfoPanel, #stableActionPanel, .confirm-box {{
  font-family: {kaiti_font} !important;
}}

/* 移除/平滑過度重之 3D 浮雕文字陰影 */
.topbar button, .topbar select, .topbar a button,
#endTurnBtn, .end-turn-btn,
#stableActionTactical, #stableActionAttack, #stableActionConfirm, #stableActionCancel,
#status, .enemy-info-title, .score-badge-label, .score-badge-num, .score-val,
.xlw-spell-activation-title, .xlw-tribute-activation-title, .xlw-coin-toss-title, .xlw-coin-toss-status-bar {{
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.6) !important;
  letter-spacing: 0.8px !important;
}}

"""

    css_content += typo_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Updated static/style_v8.css with smooth KaiTi typography successfully!")

    # Update cache-buster in static/index.html to v=11.10-smooth-kaiti-typography
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=11.10-smooth-kaiti-typography', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=11.10-smooth-kaiti-typography', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_typography()
