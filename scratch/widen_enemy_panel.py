# -*- coding: utf-8 -*-
import sys, re

def widen_panel():
    sys.stdout.reconfigure(encoding='utf-8')

    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    widen_css = """

/* ==========================================================================
   OPPONENT STATUS PANEL WIDENING & UNCLIPPED TYPOGRAPHY
   (將對手狀態欄位寬度調寬，確保完美展現牌組名稱與動態數值)
   ========================================================================== */

#xlwEnemyInfoPanel, .xlw-enemy-info-panel {
  min-width: 260px !important;
  max-width: 400px !important;
  width: max-content !important;
  padding: 14px 22px !important;
  white-space: nowrap !important;
  box-sizing: border-box !important;
}

#xlwEnemyInfoPanel .enemy-info-title {
  white-space: nowrap !important;
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
}

.enemy-stats-row {
  display: flex !important;
  gap: 10px !important;
  margin-top: 8px !important;
  width: 100% !important;
  justify-content: space-between !important;
}

.enemy-stat-badge {
  white-space: nowrap !important;
  flex: 1 !important;
  text-align: center !important;
}

"""

    css_content += widen_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("1. Appended widened opponent panel CSS to static/style_v8.css successfully!")

    # Update cache-buster in static/index.html to v=10.50-widen-enemy-panel
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=10.50-widen-enemy-panel', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=10.50-widen-enemy-panel', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("2. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    widen_panel()
