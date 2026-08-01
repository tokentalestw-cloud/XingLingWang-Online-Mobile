# -*- coding: utf-8 -*-
import sys, re

def fix_modal_injection():
    sys.stdout.reconfigure(encoding='utf-8')

    idx_path = 'static/index.html'
    idx_content = open(idx_path, encoding='utf-8').read()

    # The exact comment in index.html is Battle Cats Style Welcome Splash Screen
    target_comment = "<!-- 🐱 貓咪大戰爭風格之星靈王登入歡迎首頁 (Battle Cats Style Welcome Splash Screen) -->"
    
    if target_comment not in idx_content:
        print("ERROR: Target comment not found in index.html! Injection failed.")
        return

    replacement_code = """  <!-- 選擇出戰牌組遮罩 (Pre-Battle Deck Selection Modal) -->
  <div id="xlwPreBattleDeckSelectOverlay" class="xlw-prebattle-overlay" style="display: none !important;">
    <div class="prebattle-container">
      <h2 class="prebattle-title">⚔️ 選擇出戰陣容</h2>
      
      <!-- 我方陣營與牌組選擇 -->
      <div class="prebattle-field-group">
        <div class="prebattle-label">我方出戰陣營與類型：</div>
        <div class="prebattle-selects-row">
          <select id="modalFactionSelect" class="prebattle-select"></select>
          <select id="modalDeckSelect" class="prebattle-select"></select>
        </div>
      </div>
      
      <!-- 對手牌組選擇 (僅在單人模式顯示) -->
      <div id="prebattleEnemyGroup" class="prebattle-field-group">
        <div class="prebattle-label">對手 AI 牌組：</div>
        <select id="modalAiDeckSelect" class="prebattle-select"></select>
      </div>
      
      <!-- 確認按鈕 (位於右下角) -->
      <div class="prebattle-action-row">
        <button id="prebattleConfirmBtn" class="prebattle-confirm-btn" onclick="window.xlwConfirmPreBattle()">確認出戰 ➔</button>
      </div>
    </div>
  </div>

  <!-- 🐱 貓咪大戰爭風格之星靈王登入歡迎首頁 (Battle Cats Style Welcome Splash Screen) -->"""

    idx_content = idx_content.replace(target_comment, replacement_code)

    # Update cache-busters to v=19.99-prebattle-modal-fixed
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.99-prebattle-modal-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.99-prebattle-modal-fixed', idx_content)

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("SUCCESS: Injected pre-battle modal and updated cache-busters in index.html!")

if __name__ == '__main__':
    fix_modal_injection()
