# -*- coding: utf-8 -*-
import sys, re

def apply_topbar_and_magnification():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update index.html to restructure topbar
    idx_content = open(idx_path, encoding='utf-8').read()

    old_topbar_groups = """    <!-- 2. 返回首頁區塊 (替換原本三大入口按鈕) -->
    <div class="topbar-group action-group">
      <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 13px !important; padding: 6px 12px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important;">🏠 返回首頁</button>
    </div>

    <!-- 3. 系統設定與戰況區塊 -->
    <div class="topbar-group settings-group">
      <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
      <select id="xlwAiDiffSelect" class="topbar-setting-select" onchange="window.xlwSetAiDifficulty(this.value)">
        <option value="expert">⚡ 難度: 專家</option>
        <option value="normal">🌱 難度: 普通</option>
        <option value="nightmare">🔥 難度: 噩夢</option>
      </select>
      <button id="xlwIphone14SimBtn" class="topbar-setting-btn" onclick="window.xlwToggleIphone14Sim()" style="border-color: #ffd76a; color: #ffe600;">📱 iPhone 14 模擬</button>
      <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    </div>"""

    new_topbar_groups = """    <!-- 2. 系統設定與戰況區塊 -->
    <div class="topbar-group settings-group">
      <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
      <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    </div>

    <!-- 3. 返回首頁區塊 (放在最右邊) -->
    <div class="topbar-group action-group">
      <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 13px !important; padding: 6px 12px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important;">🏠 返回首頁</button>
    </div>"""

    idx_content = idx_content.replace(old_topbar_groups, new_topbar_groups)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Restructured topbar layout and removed difficulty/iPhone14 simulation buttons successfully!")

    # 2. Modify static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Scale preview panel to 0.80 (halved from 1.60)
    css_content = css_content.replace(
        "transform: scale(1.60) !important;",
        "transform: scale(0.80) !important;"
    )

    # Double bottom-right action panel scale from 0.64 to 1.28
    css_content = css_content.replace(
        "transform: scale(0.64) !important;\n    transform-origin: bottom right !important;",
        "transform: scale(1.28) !important;\n    transform-origin: bottom right !important;"
    )

    # Enlarge scoreboard font sizes in the landscape media query block
    old_score_fonts = """  .score-badge-label {
    font-size: 9.5px !important; /* 字體縮小 */
    color: #ffd76a !important;
  }

  .score-badge-num {
    font-size: 12px !important; /* 字體縮小 */
    font-weight: bold !important;
    color: #ffffff !important;
  }

  .score-badge-subrow {
    font-size: 8px !important; /* 字體縮小 */
    opacity: 0.85 !important;
  }"""

    new_score_fonts = """  .score-badge-label {
    font-size: 14.5px !important; /* 字體雙倍放大 */
    color: #ffd76a !important;
  }

  .score-badge-num {
    font-size: 17.0px !important; /* 字體雙倍放大 */
    font-weight: bold !important;
    color: #ffffff !important;
  }

  .score-badge-subrow {
    font-size: 12.0px !important; /* 字體雙倍放大 */
    opacity: 0.85 !important;
  }"""

    css_content = css_content.replace(old_score_fonts, new_score_fonts)

    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Resized preview panel, action panel, and scoreboard font sizes in style_v8.css successfully!")

    # 3. Update cache-buster in static/index.html to v=19.20-topbar-and-hud-perfected
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.20-topbar-and-hud-perfected', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.20-topbar-and-hud-perfected', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    apply_topbar_and_magnification()
