# -*- coding: utf-8 -*-
import sys, re

def reorganize_topbar():
    sys.stdout.reconfigure(encoding='utf-8')

    # 1. Update static/index.html topbar HTML
    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    new_topbar_html = """  <!-- 上方導航工具列 (3 大功能分組：牌組選擇 | 對戰模式 | 系統設定) -->
  <header class="topbar topbar-grouped-v9">
    <div class="topbar-brand">✨ 星靈王</div>

    <!-- 1. 牌組選擇區塊 -->
    <div class="topbar-group deck-group">
      <span class="group-label">🎴 我方:</span>
      <select id="factionSelect" aria-label="選擇種族">
        <option value="藝術品">藝術品</option>
        <option value="喵喵賊">喵喵賊</option>
        <option value="妖怪村莊">妖怪村莊</option>
        <option value="獸人">獸人</option>
        <option value="虛擬世界">虛擬世界</option>
        <option value="勇者公會">勇者公會</option>
        <option value="妖精">妖精</option>
        <option value="山羊族">山羊族</option>
        <option value="機械軍團">機械軍團</option>
        <option value="歡樂島">歡樂島</option>
        <option value="特殊旅人">特殊旅人</option>
        <option value="甜點王國">甜點王國</option>
        <option value="發電獸">發電獸</option>
        <option value="碳碳族">碳碳族</option>
        <option value="蒸汽世界">蒸汽世界</option>
        <option value="進化野人">進化野人</option>
        <option value="馬戲團">馬戲團</option>
        <option value="骷髏人">骷髏人</option>
      </select>
      <select id="deckSelect" aria-label="選擇牌組"></select>

      <span class="group-label" style="margin-left: 8px;">👾 對手:</span>
      <select id="aiDeckSelect" aria-label="選擇對手AI牌組">
        <option value="隨機">🎲 隨機牌組</option>
        <option value="妖怪村莊">妖怪村莊</option>
        <option value="發電獸">發電獸</option>
        <option value="碳碳族">碳碳族</option>
        <option value="藝術品">藝術品</option>
        <option value="喵喵賊">喵喵賊</option>
        <option value="獸人">獸人</option>
        <option value="虛擬世界">虛擬世界</option>
        <option value="勇者公會">勇者公會</option>
        <option value="歡樂島">歡樂島</option>
      </select>
    </div>

    <!-- 2. 對戰模式與按鈕區塊 -->
    <div class="topbar-group action-group">
      <button id="newGameBtn" class="topbar-action-btn primary" onclick="newGame()">🤖 單人對抗 AI</button>
      <button id="multiplayerBtn" class="topbar-action-btn online" onclick="showMultiplayerLobby()">🌐 線上雙人對決</button>
      <a href="/static/deck_builder.html?v=8.12" style="text-decoration: none;">
        <button type="button" class="topbar-action-btn builder">🛠️ 牌組編輯器</button>
      </a>
    </div>

    <!-- 3. 系統設定與戰況區塊 -->
    <div class="topbar-group settings-group">
      <button id="scoreBtn" class="topbar-setting-btn">📜 戰局紀錄</button>
      <select id="xlwAiDiffSelect" class="topbar-setting-select" onchange="window.xlwSetAiDifficulty(this.value)">
        <option value="expert">⚡ 難度: 專家</option>
        <option value="normal">🌱 難度: 普通</option>
        <option value="nightmare">🔥 難度: 噩夢</option>
      </select>
      <button id="xlwSfxToggleBtn" class="topbar-setting-btn" onclick="window.xlwToggleSFX()">🔊 音效: 開</button>
    </div>
  </header>"""

    # Replace topbar block in static/index.html
    header_start = idx_content.find('<header class="topbar')
    header_end = idx_content.find('</header>') + len('</header>')
    if header_start >= 0 and header_end > header_start:
        idx_content = idx_content[:header_start] + new_topbar_html + idx_content[header_end:]

    # Update cache-buster to v=13.30-reorganized-clean-topbar
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=13.30-reorganized-clean-topbar', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=13.30-reorganized-clean-topbar', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Reorganized static/index.html topbar into 3 clean groups successfully!")

    # 2. Append Grouped Topbar CSS to static/style_v8.css
    css_path = 'static/style_v8.css'
    css_content = open(css_path, encoding='utf-8').read()

    topbar_css = """

/* ==========================================================================
   REORGANIZED 3-MODULE GROUPED TOPBAR (最上排按鈕分組與一目瞭然高質感模組)
   ========================================================================== */

.topbar-grouped-v9 {
  height: 52px !important;
  background: linear-gradient(180deg, rgba(22, 16, 32, 0.96) 0%, rgba(10, 8, 18, 0.98) 100%) !important;
  border-bottom: 1.5px solid rgba(212, 175, 55, 0.45) !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 0 16px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.7) !important;
  z-index: 1000 !important;
  gap: 10px !important;
}

.topbar-brand {
  color: #ffe600 !important;
  font-size: 17px !important;
  font-weight: 900 !important;
  text-shadow: 0 0 10px rgba(255, 230, 0, 0.6) !important;
  white-space: nowrap !important;
}

.topbar-group {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: rgba(0, 0, 0, 0.45) !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 10px !important;
  padding: 4px 8px !important;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.4) !important;
}

.topbar-group.deck-group {
  border-color: rgba(212, 175, 55, 0.35) !important;
}

.topbar-group.action-group {
  background: rgba(255, 215, 0, 0.04) !important;
  border-color: rgba(212, 175, 55, 0.45) !important;
}

.topbar-group.settings-group {
  border-color: rgba(255, 255, 255, 0.18) !important;
}

.group-label {
  color: #fef08a !important;
  font-size: 13px !important;
  font-weight: 900 !important;
  white-space: nowrap !important;
}

.topbar-group select {
  background: rgba(20, 16, 32, 0.9) !important;
  color: #ffffff !important;
  border: 1.5px solid rgba(212, 175, 55, 0.5) !important;
  border-radius: 6px !important;
  padding: 3px 8px !important;
  font-size: 13px !important;
  font-weight: bold !important;
  cursor: pointer !important;
  outline: none !important;
}

.topbar-group select:hover {
  border-color: #ffe600 !important;
}

.topbar-action-btn {
  border-radius: 8px !important;
  padding: 5px 12px !important;
  font-size: 13px !important;
  font-weight: 900 !important;
  cursor: pointer !important;
  transition: transform 0.15s ease, box-shadow 0.15s ease !important;
  white-space: nowrap !important;
}

.topbar-action-btn.primary {
  background: linear-gradient(180deg, #473819 0%, #291e0a 100%) !important;
  color: #fef08a !important;
  border: 1.5px solid rgba(212, 175, 55, 0.7) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.3), 0 2px 6px rgba(0,0,0,0.5) !important;
}

.topbar-action-btn.online {
  background: linear-gradient(180deg, #1b3a4b 0%, #061a23 100%) !important;
  color: #a5f3fc !important;
  border: 1.5px solid rgba(56, 189, 248, 0.7) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.3), 0 2px 6px rgba(0,0,0,0.5) !important;
}

.topbar-action-btn.builder {
  background: linear-gradient(180deg, #2d1f3d 0%, #150b1f 100%) !important;
  color: #e9d5ff !important;
  border: 1.5px solid rgba(192, 132, 252, 0.7) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.3), 0 2px 6px rgba(0,0,0,0.5) !important;
}

.topbar-action-btn:hover {
  transform: translateY(-1.5px) !important;
}

.topbar-setting-btn, .topbar-setting-select {
  background: rgba(255, 255, 255, 0.08) !important;
  color: #f3f4f6 !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  border-radius: 6px !important;
  padding: 4px 10px !important;
  font-size: 12.5px !important;
  font-weight: bold !important;
  cursor: pointer !important;
  white-space: nowrap !important;
}

.topbar-setting-btn:hover, .topbar-setting-select:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: #ffffff !important;
}

"""

    css_content += topbar_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended Grouped Topbar CSS to static/style_v8.css successfully!")

if __name__ == '__main__':
    reorganize_topbar()
