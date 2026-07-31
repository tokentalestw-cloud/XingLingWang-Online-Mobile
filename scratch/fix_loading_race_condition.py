# -*- coding: utf-8 -*-
import sys, re

def fix_loading_race():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    idx_path = 'static/index.html'

    # 1. Update static/index.html to disable buttons initially and show loading state
    idx_content = open(idx_path, encoding='utf-8').read()

    old_ai_btn = '<button class="menu-btn menu-ai" onclick="window.xlwChooseMode(\'single\')">'
    new_ai_btn = '<button class="menu-btn menu-ai" id="xlwWelcomeAiBtn" onclick="window.xlwChooseMode(\'single\')" disabled style="opacity: 0.55; cursor: not-allowed;">'

    old_multi_btn = '<button class="menu-btn menu-multi" onclick="window.xlwChooseMode(\'multi\')">'
    new_multi_btn = '<button class="menu-btn menu-multi" id="xlwWelcomeMultiBtn" onclick="window.xlwChooseMode(\'multi\')" disabled style="opacity: 0.55; cursor: not-allowed;">'

    idx_content = idx_content.replace(old_ai_btn, new_ai_btn)
    idx_content = idx_content.replace(old_multi_btn, new_multi_btn)

    # Change the initial text to "載入中..."
    idx_content = idx_content.replace('<span class="btn-text">單人對抗 AI</span>', '<span class="btn-text" id="xlwAiBtnText">載入中...</span>')
    idx_content = idx_content.replace('<span class="btn-text">線上雙人對決</span>', '<span class="btn-text" id="xlwMultiBtnText">載入中...</span>')

    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("1. Set initial loading disabled state for welcome buttons in index.html successfully!")

    # 2. Update static/game_v8.js to set window.XLW_gameInProgress = true in newGame and enable buttons in init
    js_content = open(js_path, encoding='utf-8').read()

    # Set window.XLW_gameInProgress = true in newGame
    old_newgame_start = "function newGame() {\n  // 確保重設為單人對抗 AI 模式"
    new_newgame_start = "function newGame() {\n  window.XLW_gameInProgress = true;\n  // 確保重設為單人對抗 AI 模式"
    js_content = js_content.replace(old_newgame_start, new_newgame_start)

    # Enable buttons at the end of init()
    # Let's locate the try block ending before room params resolution in init()
    # Around line 621: "    // 解析線上房間參數"
    old_init_end = "    // 解析線上房間參數"
    enable_buttons_js = """    // 解除首頁按鈕的載入鎖定
    try {
      const aiBtn = document.getElementById("xlwWelcomeAiBtn");
      const multiBtn = document.getElementById("xlwWelcomeMultiBtn");
      const aiText = document.getElementById("xlwAiBtnText");
      const multiText = document.getElementById("xlwMultiBtnText");

      if (aiBtn) {
        aiBtn.disabled = false;
        aiBtn.style.opacity = "1";
        aiBtn.style.cursor = "pointer";
      }
      if (multiBtn) {
        multiBtn.disabled = false;
        multiBtn.style.opacity = "1";
        multiBtn.style.cursor = "pointer";
      }
      if (aiText) aiText.textContent = "單人對抗 AI";
      if (multiText) multiText.textContent = "線上雙人對決";
      console.log("Welcome buttons unlocked: card database loaded successfully!");
    } catch (eUnlock) {
      console.warn("Failed to unlock welcome buttons:", eUnlock);
    }

    // 解析線上房間參數"""

    js_content = js_content.replace(old_init_end, enable_buttons_js)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("2. Injected welcome button enabler and gameInProgress flags in game_v8.js successfully!")

    # Update cache-buster in static/index.html to v=17.60-race-condition-fixed
    idx_content = open(idx_path, encoding='utf-8').read()
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=17.60-race-condition-fixed', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=17.60-race-condition-fixed', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Updated static/index.html cache-buster successfully!")

if __name__ == '__main__':
    fix_loading_race()
