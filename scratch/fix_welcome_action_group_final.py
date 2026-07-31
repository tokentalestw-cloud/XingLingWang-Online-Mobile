# -*- coding: utf-8 -*-
import sys, re

def fix_action_group():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update static/index.html to replace the old action buttons with the "🏠 返回首頁" button
    idx_content = open(idx_path, encoding='utf-8').read()

    # Clean old Return to Title buttons if they were added as duplicates
    idx_content = idx_content.replace('<button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #1c152a 0%, #2c2244 100%) !important; border: 1px solid #ffd76a !important; color: #ffd76a !important; font-weight: bold !important;">🏠 返回首頁</button>', '')
    idx_content = idx_content.replace('<button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #1c152a 0%, #2c2244 100%) !important; border: 1px solid #ffd76a !important; color: #ffd76a !important; font-weight: bold !important;">🏠 返回主選單</button>', '')

    # Locate the old action-group and replace its content with the single "🏠 返回首頁" button
    old_action_group_pattern = r'<!-- 2\. 對戰模式與按鈕區塊 -->\s*<div class="topbar-group action-group">.*?</div>'
    new_action_group = """<!-- 2. 返回首頁區塊 (替換原本三大入口按鈕) -->
    <div class="topbar-group action-group">
      <button id="xlwReturnTitleBtn" class="topbar-action-btn" onclick="window.xlwReturnToTitle()" style="background: linear-gradient(135deg, #3c1e5c 0%, #1c0e2b 100%) !important; border: 2px solid #ffd76a !important; color: #ffe600 !important; font-weight: bold !important; font-size: 13px !important; padding: 6px 12px !important; border-radius: 50px !important; box-shadow: 0 0 10px rgba(255, 215, 106, 0.3) !important; cursor: pointer !important;">🏠 返回首頁</button>
    </div>"""

    idx_content = re.sub(old_action_group_pattern, new_action_group, idx_content, flags=re.DOTALL)
    
    # Write updated index.html
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Successfully replaced action-group with Return to Home button in index.html!")

    # 2. Update static/game_v8.js to use global functions and check selector IDs
    js_content = open(js_path, encoding='utf-8').read()

    # Search for xlwChooseMode definition and replace it
    choose_mode_pattern = r'window\.xlwChooseMode\s*=\s*function\(mode\)\s*\{.*?\};'
    
    new_choose_mode_js = """window.xlwChooseMode = function(mode) {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.display = "none";
    }, 450);
  }
  
  if (mode === 'single') {
    // 進入單人對決模式，直接調用全域的 newGame 啟動對戰
    if (typeof newGame === 'function') {
      newGame();
    } else {
      const newGameBtn = document.getElementById("newGameBtn");
      if (newGameBtn) newGameBtn.click();
    }
    console.log("Single-player AI Mode launched!");
  } else if (mode === 'multi') {
    // 進入線上雙人對決模式，直接調用全域的 showMultiplayerLobby 啟動大廳
    if (typeof showMultiplayerLobby === 'function') {
      showMultiplayerLobby();
    } else {
      const multiplayerBtn = document.getElementById("multiplayerBtn");
      if (multiplayerBtn) multiplayerBtn.click();
    }
    console.log("Online Multiplayer Mode launched!");
  }
};"""

    js_content = re.sub(choose_mode_pattern, new_choose_mode_js, js_content, flags=re.DOTALL)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Successfully updated welcome selection routing in game_v8.js!")

    # Update cache-buster in static/index.html to v=17.30-welcome-action-group-fixed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.30-welcome-action-group-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.30-welcome-action-group-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_action_group()
