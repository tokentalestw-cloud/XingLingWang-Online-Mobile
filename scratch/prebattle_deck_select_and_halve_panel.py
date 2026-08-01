# -*- coding: utf-8 -*-
import sys, re

def prebattle_deck_select():
    sys.stdout.reconfigure(encoding='utf-8')

    js_path = 'static/game_v8.js'
    css_path = 'static/style_v8.css'
    idx_path = 'static/index.html'

    # 1. Update renderEnemyPanel and xlwChooseMode / xlwConfirmPreBattle in static/game_v8.js
    js_content = open(js_path, encoding='utf-8').read()

    # Re-write renderEnemyPanel to show "對手手牌" on a single line inside 55px width
    old_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 13px !important; white-space: nowrap; font-weight: bold; color: #ffd76a;">👾 對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 4px;">
      <div class="enemy-stat-badge" style="font-size: 15px !important; font-weight: bold; color: #ff7875 !important; padding: 2px 6px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.25) !important; border-radius: 4px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span> 張</div>
    </div>
  `;
}"""

    new_render_enemy = """function renderEnemyPanel() {
  const panel = $("xlwEnemyInfoPanel") || (() => {
    const div = document.createElement("div");
    div.id = "xlwEnemyInfoPanel";
    div.className = "xlw-enemy-info-panel";
    document.body.appendChild(div);
    return div;
  })();

  panel.innerHTML = `
    <div class="enemy-info-title" style="text-align: center; font-size: 10px !important; white-space: nowrap; font-weight: bold; color: #ffd76a; line-height: 1;">對手手牌</div>
    <div class="enemy-stats-row" style="display: flex; justify-content: center; margin-top: 2px;">
      <div class="enemy-stat-badge" style="font-size: 13px !important; font-weight: bold; color: #ff7875 !important; padding: 1px 4px !important; margin: 0 !important; white-space: nowrap; border: 0.5px solid rgba(255, 215, 106, 0.2) !important; border-radius: 3px !important;"><span id="enemyHandCountInfo">${window.XLW_ENEMY.hand.length}</span>張</div>
    </div>
  `;
}"""

    js_content = js_content.replace(old_render_enemy, new_render_enemy)

    # Re-write window.xlwChooseMode and define window.xlwConfirmPreBattle
    old_choose_mode = """window.xlwChooseMode = function(mode) {
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.setProperty("display", "none", "important");
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

    new_choose_mode = """window.xlwChooseMode = function(mode) {
  window.XLW_ACTIVE_MODE = mode;
  
  const modal = document.getElementById("xlwPreBattleDeckSelectOverlay");
  if (!modal) return;
  
  // Populate Factions
  const factionSelect = document.getElementById("factionSelect");
  const modalFactionSelect = document.getElementById("modalFactionSelect");
  if (factionSelect && modalFactionSelect) {
    modalFactionSelect.innerHTML = factionSelect.innerHTML;
    modalFactionSelect.value = factionSelect.value;
  }
  
  // Populate Decks
  const deckSelect = document.getElementById("deckSelect");
  const modalDeckSelect = document.getElementById("modalDeckSelect");
  if (deckSelect && modalDeckSelect) {
    modalDeckSelect.innerHTML = deckSelect.innerHTML;
    modalDeckSelect.value = deckSelect.value;
  }
  
  // Populate Opponent Decks
  const aiDeckSelect = document.getElementById("aiDeckSelect");
  const modalAiDeckSelect = document.getElementById("modalAiDeckSelect");
  if (aiDeckSelect && modalAiDeckSelect) {
    modalAiDeckSelect.innerHTML = aiDeckSelect.innerHTML;
    modalAiDeckSelect.value = aiDeckSelect.value;
  }
  
  // Set up event listeners for faction selection changes
  if (modalFactionSelect && modalDeckSelect && factionSelect && deckSelect) {
    modalFactionSelect.onchange = () => {
      factionSelect.value = modalFactionSelect.value;
      // Trigger base select change to update deck dropdown
      const event = new Event('change');
      factionSelect.dispatchEvent(event);
      // Wait a fraction of a millisecond and copy options
      setTimeout(() => {
        modalDeckSelect.innerHTML = deckSelect.innerHTML;
        modalDeckSelect.value = deckSelect.value;
      }, 10);
    };
  }
  
  // Toggle enemy selection group
  const enemyGroup = document.getElementById("prebattleEnemyGroup");
  if (enemyGroup) {
    enemyGroup.style.display = (mode === 'single') ? "block" : "none";
  }
  
  // Show the modal
  modal.style.setProperty("display", "flex", "important");
};

window.xlwConfirmPreBattle = function() {
  const modal = document.getElementById("xlwPreBattleDeckSelectOverlay");
  if (modal) {
    modal.style.setProperty("display", "none", "important");
  }
  
  const overlay = document.getElementById("xlwWelcomeOverlay");
  if (overlay) {
    overlay.classList.add("xlw-welcome-fadeout");
    setTimeout(() => {
      overlay.style.setProperty("display", "none", "important");
    }, 450);
  }
  
  // Apply final selections to original selectors
  const modalFactionSelect = document.getElementById("modalFactionSelect");
  const factionSelect = document.getElementById("factionSelect");
  if (modalFactionSelect && factionSelect) {
    factionSelect.value = modalFactionSelect.value;
  }
  
  const modalDeckSelect = document.getElementById("modalDeckSelect");
  const deckSelect = document.getElementById("deckSelect");
  if (modalDeckSelect && deckSelect) {
    deckSelect.value = modalDeckSelect.value;
  }
  
  const modalAiDeckSelect = document.getElementById("modalAiDeckSelect");
  const aiDeckSelect = document.getElementById("aiDeckSelect");
  if (modalAiDeckSelect && aiDeckSelect) {
    aiDeckSelect.value = modalAiDeckSelect.value;
  }
  
  const mode = window.XLW_ACTIVE_MODE;
  if (mode === 'single') {
    if (typeof newGame === 'function') {
      newGame();
    } else {
      const newGameBtn = document.getElementById("newGameBtn");
      if (newGameBtn) newGameBtn.click();
    }
  } else if (mode === 'multi') {
    if (typeof showMultiplayerLobby === 'function') {
      showMultiplayerLobby();
    } else {
      const multiplayerBtn = document.getElementById("multiplayerBtn");
      if (multiplayerBtn) multiplayerBtn.click();
    }
  }
};"""

    js_content = js_content.replace(old_choose_mode, new_choose_mode)
    open(js_path, 'w', encoding='utf-8').write(js_content)
    print("1. Injected Pre-Battle selection logic into game_v8.js successfully!")

    # 2. Modify static/style_v8.css
    css_content = open(css_path, encoding='utf-8').read()

    # Re-style #xlwEnemyInfoPanel in style_v8.css landscape block (width 55px, padding 3px 4px)
    old_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 180px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 6px !important;
    margin: 0 !important;
    display: block !important;
    width: 110px !important;
  }"""

    new_enemy_style = """  #xlwEnemyInfoPanel {
    position: absolute !important;
    left: 180px !important;
    top: 32px !important;
    right: auto !important;
    bottom: auto !important;
    z-index: 10000 !important;
    transform: scale(0.72) !important;
    transform-origin: top left !important;
    background: rgba(15, 10, 25, 0.85) !important;
    border: 0.5px solid rgba(255, 215, 106, 0.3) !important;
    border-radius: 8px !important;
    padding: 3px 4px !important;
    margin: 0 !important;
    display: block !important;
    width: 55px !important;
  }"""

    css_content = css_content.replace(old_enemy_style, new_enemy_style)

    # Append Pre-battle Modal Styles
    prebattle_css = """

/* ===== 選擇出戰牌組遮罩樣式 (Pre-battle Modal) ===== */
.xlw-prebattle-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  background: rgba(8, 6, 15, 0.96) !important;
  backdrop-filter: blur(15px) !important;
  z-index: 999999 !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
}

.prebattle-container {
  background: linear-gradient(145deg, rgba(30, 20, 45, 0.98) 0%, rgba(15, 10, 25, 0.99) 100%) !important;
  border: 1.5px solid rgba(255, 215, 106, 0.45) !important;
  border-radius: 20px !important;
  padding: 24px 30px !important;
  width: 460px !important;
  max-width: 90% !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8), 0 0 30px rgba(255, 215, 106, 0.15) !important;
  position: relative !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 16px !important;
}

.prebattle-title {
  margin: 0 0 8px 0 !important;
  font-size: 20px !important;
  font-weight: bold !important;
  text-align: center !important;
  color: #ffd76a !important;
  text-shadow: 0 0 10px rgba(255, 215, 106, 0.4) !important;
}

.prebattle-field-group {
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
}

.prebattle-label {
  font-size: 13px !important;
  font-weight: bold !important;
  color: #ffe6a0 !important;
}

.prebattle-selects-row {
  display: flex !important;
  gap: 10px !important;
}

.prebattle-select {
  flex: 1 !important;
  height: 38px !important;
  font-size: 14px !important;
  padding: 6px 10px !important;
  border-radius: 8px !important;
  border: 1px solid rgba(255, 215, 106, 0.4) !important;
  background: rgba(20, 16, 32, 0.85) !important;
  color: #ffffff !important;
  font-weight: bold !important;
  outline: none !important;
}

.prebattle-select:focus {
  border-color: #ffd76a !important;
  box-shadow: 0 0 8px rgba(255, 215, 106, 0.3) !important;
}

.prebattle-action-row {
  display: flex !important;
  justify-content: flex-end !important;
  margin-top: 10px !important;
}

.prebattle-confirm-btn {
  background: linear-gradient(135deg, #a67c1e 0%, #d4af37 50%, #f9d976 100%) !important;
  border: 1px solid #ffffff !important;
  color: #0b0713 !important;
  font-weight: 900 !important;
  font-size: 15px !important;
  padding: 8px 20px !important;
  border-radius: 50px !important;
  cursor: pointer !important;
  box-shadow: 0 4px 15px rgba(212, 175, 55, 0.4) !important;
  transition: all 0.2s ease !important;
}

.prebattle-confirm-btn:hover {
  transform: scale(1.05) !important;
  box-shadow: 0 6px 20px rgba(212, 175, 55, 0.6) !important;
}
"""
    css_content += prebattle_css
    open(css_path, 'w', encoding='utf-8').write(css_content)
    print("2. Appended pre-battle styles in style_v8.css successfully!")

    # 3. Modify static/index.html: Inject modal structure
    idx_content = open(idx_path, encoding='utf-8').read()

    prebattle_html = """  <!-- 歡迎模式選擇浮層 (PWA/Welcome Screen Overlay) -->"""

    prebattle_modal_code = """  <!-- 選擇出戰牌組遮罩 (Pre-Battle Deck Selection Modal) -->
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

  <!-- 歡迎模式選擇浮層 (PWA/Welcome Screen Overlay) -->"""

    idx_content = idx_content.replace(prebattle_html, prebattle_modal_code)

    # Update cache-busters in static/index.html to v=19.99-prebattle-deck-select-ready
    idx_content = re.sub(r'game_v8\.js\?v=[^"\']+', 'game_v8.js?v=19.99-prebattle-deck-select-ready', idx_content)
    idx_content = re.sub(r'style_v8\.css\?v=[^"\']+', 'style_v8.css?v=19.99-prebattle-deck-select-ready', idx_content)
    open(idx_path, 'w', encoding='utf-8').write(idx_content)
    print("3. Injected pre-battle modal html structure and updated cache-busters in static/index.html successfully!")

if __name__ == '__main__':
    prebattle_deck_select()
